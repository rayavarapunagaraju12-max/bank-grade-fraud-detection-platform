from neo4j import GraphDatabase

from backend.config import get_settings


class GraphBuilder:
    fallback_edges: dict[str, set[tuple[str, str]]] = {}

    def __init__(self) -> None:
        settings = get_settings()
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
        self.use_neo4j = True

    def ensure_schema(self) -> None:
        statements = [
            "CREATE CONSTRAINT account_id IF NOT EXISTS FOR (n:Account) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT device_id IF NOT EXISTS FOR (n:Device) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT ip_id IF NOT EXISTS FOR (n:IP) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT merchant_id IF NOT EXISTS FOR (n:Merchant) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT beneficiary_id IF NOT EXISTS FOR (n:Beneficiary) REQUIRE n.id IS UNIQUE",
        ]
        try:
            with self.driver.session() as session:
                for stmt in statements:
                    session.run(stmt)
        except Exception:
            self.use_neo4j = False

    def upsert_transaction(self, txn: dict) -> None:
        if not self.use_neo4j:
            self._upsert_memory(txn)
            return
        params = {**txn, "beneficiary_id": txn.get("beneficiary_id") or "unknown"}
        is_known_fraud = bool(txn.get("is_fraud") or txn.get("known_fraud") or txn.get("fraud_label"))
        query = """
        MERGE (a:Account {id: $account_id})
        SET a.known_fraud = coalesce(a.known_fraud, false) OR $is_known_fraud
        MERGE (d:Device {id: $device_id})
        MERGE (ip:IP {id: $ip_address})
        MERGE (m:Merchant {id: $merchant_id})
        MERGE (b:Beneficiary {id: $beneficiary_id})
        MERGE (a)-[:USED_DEVICE]->(d)
        MERGE (a)-[:USED_IP]->(ip)
        MERGE (a)-[:PAID_MERCHANT]->(m)
        MERGE (a)-[:PAID_BENEFICIARY]->(b)
        """
        try:
            with self.driver.session() as session:
                session.run(query, **params, is_known_fraud=is_known_fraud)
        except Exception:
            self.use_neo4j = False
            self._upsert_memory(txn)

    def _upsert_memory(self, txn: dict) -> None:
        account = txn["account_id"]
        is_known_fraud = bool(txn.get("is_fraud") or txn.get("known_fraud") or txn.get("fraud_label"))
        fraud_marker = ("KNOWN_FRAUD", account) if is_known_fraud else None
        edges = {
            ("USED_DEVICE", txn["device_id"]),
            ("USED_IP", txn["ip_address"]),
            ("PAID_MERCHANT", txn["merchant_id"]),
            ("PAID_BENEFICIARY", txn.get("beneficiary_id") or "unknown"),
        }
        if fraud_marker:
            edges.add(fraud_marker)
        GraphBuilder.fallback_edges.setdefault(account, set()).update(
            edges
        )
