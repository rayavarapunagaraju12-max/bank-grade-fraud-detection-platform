import json

import redis
from neo4j import GraphDatabase

from backend.config import get_settings
from graph.graph_builder.builder import GraphBuilder


class GraphFeatureService:
    def __init__(self) -> None:
        settings = get_settings()
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
        self.use_neo4j = True
        self.cache_ttl_seconds = 120
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            self.redis.ping()
            self.use_cache = True
        except Exception:
            self.redis = None
            self.use_cache = False

    def compute(self, txn: dict) -> dict:
        cache_key = f"graph_features:{txn['account_id']}:{txn.get('device_id')}:{txn.get('ip_address')}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        if not self.use_neo4j:
            result = self._compute_memory(txn)
            self._cache_set(cache_key, result)
            return result
        account = txn["account_id"]
        query = """
        MATCH (a:Account {id: $account})
        OPTIONAL MATCH (a)--(n)
        WITH a, count(DISTINCT n) AS degree
        OPTIONAL MATCH (:Account)-[:USED_DEVICE]->(d:Device)<-[:USED_DEVICE]-(a)
        WITH a, degree, count(DISTINCT d) AS shared_devices
        OPTIONAL MATCH (:Account)-[:USED_IP]->(ip:IP)<-[:USED_IP]-(a)
        WITH a, degree, shared_devices, count(DISTINCT ip) AS shared_ips
        OPTIONAL MATCH (linked:Account)--(shared)--(a)
        WHERE linked <> a AND (shared:Device OR shared:IP)
        WITH a, degree, shared_devices, shared_ips, count(DISTINCT linked) AS linked_accounts
        OPTIONAL MATCH p=shortestPath((a)-[*..4]-(:Account {known_fraud: true}))
        RETURN degree, shared_devices, shared_ips, linked_accounts, coalesce(length(p), 99) AS distance
        """
        try:
            with self.driver.session() as session:
                row = session.run(query, account=account).single()
        except Exception:
            self.use_neo4j = False
            result = self._compute_memory(txn)
            self._cache_set(cache_key, result)
            return result
        if not row:
            result = {
                "graph_degree": 0,
                "graph_community": 0,
                "shortest_path_to_fraud": 99,
                "shared_device_count": 0,
                "shared_ip_count": 0,
                "linked_account_count": 0,
                "fraud_ring_score": 0,
            }
            self._cache_set(cache_key, result)
            return result
        community = abs(hash(account)) % 32
        ring_score = self._ring_score(
            float(row["degree"] or 0),
            int(row["shared_devices"] or 0),
            int(row["shared_ips"] or 0),
            int(row["linked_accounts"] or 0),
            float(row["distance"] or 99),
        )
        result = {
            "graph_degree": float(row["degree"] or 0),
            "graph_community": community,
            "shortest_path_to_fraud": float(row["distance"] or 99),
            "shared_device_count": int(row["shared_devices"] or 0),
            "shared_ip_count": int(row["shared_ips"] or 0),
            "linked_account_count": int(row["linked_accounts"] or 0),
            "fraud_ring_score": ring_score,
        }
        self._cache_set(cache_key, result)
        return result

    def subgraph(self, account_id: str) -> dict:
        if not self.use_neo4j:
            return self._subgraph_memory(account_id)
        query = """
        MATCH (a:Account {id: $account_id})-[r]-(n)
        RETURN a.id AS source, type(r) AS relationship, labels(n)[0] AS target_type, n.id AS target
        LIMIT 100
        """
        try:
            with self.driver.session() as session:
                rows = list(session.run(query, account_id=account_id))
        except Exception:
            self.use_neo4j = False
            return self._subgraph_memory(account_id)
        nodes = [{"id": account_id, "label": account_id, "type": "Account"}]
        edges = []
        seen = {account_id}
        for row in rows:
            if row["target"] not in seen:
                nodes.append({"id": row["target"], "label": row["target"], "type": row["target_type"]})
                seen.add(row["target"])
            edges.append({"source": row["source"], "target": row["target"], "label": row["relationship"]})
        return {"nodes": nodes, "edges": edges}

    def _compute_memory(self, txn: dict) -> dict:
        account = txn["account_id"]
        edges = GraphBuilder.fallback_edges.get(account, set())
        device = txn.get("device_id")
        ip = txn.get("ip_address")
        known_fraud_accounts = {
            acct
            for acct, account_edges in GraphBuilder.fallback_edges.items()
            if ("KNOWN_FRAUD", acct) in account_edges
        }
        linked_accounts = {
            acct
            for acct, account_edges in GraphBuilder.fallback_edges.items()
            if ("USED_DEVICE", device) in account_edges or ("USED_IP", ip) in account_edges
        }
        shared_device = sum(
            1
            for account_edges in GraphBuilder.fallback_edges.values()
            if ("USED_DEVICE", device) in account_edges
        )
        shared_ip = sum(
            1
            for account_edges in GraphBuilder.fallback_edges.values()
            if ("USED_IP", ip) in account_edges
        )
        distance_to_fraud = 1 if account in known_fraud_accounts else 99
        if distance_to_fraud == 99 and linked_accounts & known_fraud_accounts:
            distance_to_fraud = 2
        linked_count = len(linked_accounts)
        degree = float(len(edges))
        shared_device_count = max(0, shared_device - 1)
        shared_ip_count = max(0, shared_ip - 1)
        return {
            "graph_degree": degree,
            "graph_community": abs(hash(account)) % 32,
            "shortest_path_to_fraud": distance_to_fraud,
            "shared_device_count": shared_device_count,
            "shared_ip_count": shared_ip_count,
            "linked_account_count": linked_count,
            "fraud_ring_score": self._ring_score(
                degree, shared_device_count, shared_ip_count, linked_count, float(distance_to_fraud)
            ),
        }

    def _subgraph_memory(self, account_id: str) -> dict:
        nodes = [{"id": account_id, "label": account_id, "type": "Account"}]
        edges = []
        seen = {account_id}
        for relationship, target in GraphBuilder.fallback_edges.get(account_id, set()):
            if target not in seen:
                node_type = relationship.replace("USED_", "").replace("PAID_", "").title()
                nodes.append({"id": target, "label": target, "type": node_type})
                seen.add(target)
            edges.append({"source": account_id, "target": target, "label": relationship})
        return {"nodes": nodes, "edges": edges}

    def _cache_get(self, key: str) -> dict | None:
        if not self.use_cache or self.redis is None:
            return None
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            self.use_cache = False
            return None

    def _cache_set(self, key: str, value: dict) -> None:
        if not self.use_cache or self.redis is None:
            return
        try:
            self.redis.setex(key, self.cache_ttl_seconds, json.dumps(value))
        except Exception:
            self.use_cache = False

    @staticmethod
    def _ring_score(
        graph_degree: float,
        shared_devices: int,
        shared_ips: int,
        linked_accounts: int,
        distance_to_fraud: float,
    ) -> float:
        score = (
            min(graph_degree / 30, 0.25)
            + min(shared_devices / 10, 0.25)
            + min(shared_ips / 10, 0.2)
            + min(linked_accounts / 20, 0.2)
        )
        if distance_to_fraud <= 2:
            score += 0.1
        return round(max(0.0, min(1.0, score)), 4)
