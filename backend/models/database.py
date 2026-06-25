from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from backend.config import get_settings


class Base(DeclarativeBase):
    pass


class TransactionRecord(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[float] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class AlertRecord(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String, index=True)
    score: Mapped[float] = mapped_column(Float, index=True)
    risk_band: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="open", index=True)
    assigned_to: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    decision: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    decision_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    actor: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String, index=True)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class UserRecord(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    password_hash: Mapped[str] = mapped_column(String)
    roles: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[int] = mapped_column(Integer, default=1, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class DeadLetterRecord(Base):
    __tablename__ = "dead_letters"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    source_topic: Mapped[str] = mapped_column(String, index=True)
    error: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)
    metadata_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String, default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class WatchlistEntryRecord(Base):
    __tablename__ = "watchlist_entries"

    entry_id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, index=True)
    list_name: Mapped[str] = mapped_column(String, index=True)
    entity_type: Mapped[str] = mapped_column(String, default="unknown", index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    normalized_name: Mapped[str] = mapped_column(String, index=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    identifiers: Mapped[dict] = mapped_column(JSON, default=dict)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class WatchlistIngestionRecord(Base):
    __tablename__ = "watchlist_ingestions"

    ingestion_id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, index=True)
    records_seen: Mapped[int] = mapped_column(Integer, default=0)
    records_loaded: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list] = mapped_column(JSON, default=list)
    metadata_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ComplianceReportRecord(Base):
    __tablename__ = "compliance_reports"

    report_id: Mapped[str] = mapped_column(String, primary_key=True)
    report_type: Mapped[str] = mapped_column(String, index=True)
    jurisdiction: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, index=True)
    subject_account: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    validation: Mapped[dict] = mapped_column(JSON, default=dict)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ModelVersionRecord(Base):
    __tablename__ = "model_versions"

    model_id: Mapped[str] = mapped_column(String, primary_key=True)
    model_name: Mapped[str] = mapped_column(String, index=True)
    version: Mapped[str] = mapped_column(String, index=True)
    artifact_path: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="draft", index=True)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


settings = get_settings()
engine_kwargs: dict[str, object] = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_database() -> None:
    Base.metadata.create_all(bind=engine)


def get_session():
    with SessionLocal() as session:
        yield session


def persist_transaction(session: Session, payload: dict) -> None:
    record = TransactionRecord(
        transaction_id=payload["transaction_id"],
        account_id=payload["account_id"],
        amount=float(payload["amount"]),
        payload=payload,
    )
    session.merge(record)
    session.commit()
