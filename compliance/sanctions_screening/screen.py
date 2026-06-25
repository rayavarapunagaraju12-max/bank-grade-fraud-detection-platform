from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from backend.models.database import WatchlistEntryRecord
from compliance.watchlist_ingestion.service import normalize_name


@dataclass(frozen=True)
class WatchlistEntry:
    name: str
    list_name: str
    source: str


HIGH_RISK_COUNTRIES = {"CU", "IR", "KP", "RU", "SY"}
WATCHLIST = [
    WatchlistEntry("Kim Jong Un", "OFAC_SDN_DEMO", "ofac.treasury.gov"),
    WatchlistEntry("Viktor Petrov", "INTERNAL_HIGH_RISK_DEMO", "internal-risk-list"),
    WatchlistEntry("North Korea Trading Corp", "OFAC_SDN_DEMO", "ofac.treasury.gov"),
]


class SanctionsScreeningService:
    """Evidence-first sanctions screening suitable for demos and offline development.

    The bundled watchlist is intentionally small and marked as demo data. Production
    deployment should replace it with scheduled OFAC, EU, UN, and UK HMT feeds.
    """

    def screen(self, name: str | None, country: str | None, session: Session | None = None) -> dict:
        normalized_name = (name or "").strip()
        normalized_country = (country or "").strip().upper()
        name_matches = self._name_matches(normalized_name, session)
        country_hit = normalized_country in HIGH_RISK_COUNTRIES

        confidence = 0.0
        rule_triggered = None
        if name_matches:
            confidence = max(match["similarity"] for match in name_matches)
            rule_triggered = "SANCTIONS_NAME_MATCH"
        if country_hit and confidence < 0.8:
            confidence = 0.8
            rule_triggered = "HIGH_RISK_COUNTRY"

        return {
            "screened_name": normalized_name,
            "screened_country": normalized_country,
            "name_matches": name_matches,
            "country_risk": country_hit,
            "confidence": round(confidence, 4),
            "rule_triggered": rule_triggered,
            "watchlist_mode": "database-backed" if session is not None else "demo-offline",
        }

    def _name_matches(self, name: str, session: Session | None = None) -> list[dict]:
        if not name:
            return []
        matches = []
        for entry in WATCHLIST:
            similarity = SequenceMatcher(None, name.lower(), entry.name.lower()).ratio()
            if similarity >= 0.82 or name.lower() in entry.name.lower():
                matches.append(
                    {
                        "name": entry.name,
                        "list": entry.list_name,
                        "source": entry.source,
                        "similarity": round(similarity, 4),
                    }
                )
        if session is not None:
            matches.extend(self._database_matches(name, session))
        return sorted(matches, key=lambda item: item["similarity"], reverse=True)

    def _database_matches(self, name: str, session: Session) -> list[dict]:
        normalized = normalize_name(name)
        if not normalized:
            return []
        rows = session.query(WatchlistEntryRecord).limit(5000).all()
        matches = []
        for row in rows:
            candidates = [row.name, *(row.aliases or [])]
            best = max(SequenceMatcher(None, normalized, normalize_name(candidate)).ratio() for candidate in candidates)
            if best >= 0.82 or normalized in row.normalized_name:
                matches.append(
                    {
                        "name": row.name,
                        "list": row.list_name,
                        "source": row.source,
                        "entity_type": row.entity_type,
                        "country": row.country,
                        "similarity": round(best, 4),
                        "entry_id": row.entry_id,
                    }
                )
        return matches
