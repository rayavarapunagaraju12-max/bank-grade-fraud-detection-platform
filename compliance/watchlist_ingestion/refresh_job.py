from backend.models.database import SessionLocal, init_database
from compliance.audit_logs.audit import write_audit_log
from compliance.watchlist_ingestion.service import ingest_official_feeds


def main() -> None:
    init_database()
    with SessionLocal() as session:
        result = ingest_official_feeds(session)
        write_audit_log(session, "watchlist-refresh-job", "official_watchlists_refreshed", "watchlists", result)
        session.commit()
        print(result)


if __name__ == "__main__":
    main()
