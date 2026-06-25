from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class Channel(str, Enum):
    card_present = "card_present"
    card_not_present = "card_not_present"
    wire = "wire"
    ach = "ach"
    atm = "atm"


class TransactionIn(BaseModel):
    transaction_id: str = Field(..., examples=["txn_000001"])
    account_id: str = Field(..., examples=["acct_123"])
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    merchant_id: str
    merchant_category: str = "general"
    device_id: str
    ip_address: str
    beneficiary_id: str | None = None
    channel: Channel = Channel.card_not_present
    country: str = "US"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FeatureVector(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    account_velocity_5m: int = 0
    account_velocity_1h: int = 0
    avg_amount_1h: float = 0
    merchant_frequency_24h: int = 0
    device_reuse_24h: int = 0
    ip_reuse_24h: int = 0
    beneficiary_frequency_24h: int = 0
    graph_degree: float = 0
    graph_community: int = 0
    shortest_path_to_fraud: float = 99
    shared_device_count: int = 0
    shared_ip_count: int = 0
    fraud_ring_score: float = 0
    linked_account_count: int = 0


class FraudScore(BaseModel):
    transaction_id: str
    fraud_score: float
    risk_band: str
    tabular_score: float
    anomaly_score: float
    graph_score: float
    explanation: dict
    narrative: str | None = None


class Alert(BaseModel):
    alert_id: str
    transaction: TransactionIn
    score: FraudScore
    status: str = "open"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
