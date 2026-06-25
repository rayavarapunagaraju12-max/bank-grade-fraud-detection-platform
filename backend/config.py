from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    enable_api_key_auth: bool = False
    demo_api_key: str = "demo-client-key"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_enabled: bool = False
    transactions_topic: str = "transactions"
    features_topic: str = "features"
    alerts_topic: str = "fraud-alerts"
    dlq_topic: str = "transactions-dlq"
    kafka_consumer_group: str = "fraud-detection"

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+psycopg://fraud:fraud_password@localhost:5432/fraud"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "fraud_graph_password"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "fraudadmin"
    minio_secret_key: str = "fraudadmin123"
    minio_bucket: str = "models"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    generate_llm_narrative_inline: bool = False
    cors_origins: str = "http://localhost:5173"
    ofac_sdn_csv_url: str = "https://www.treasury.gov/ofac/downloads/sdn.csv"
    unsc_consolidated_xml_url: str = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
    eu_consolidated_xml_url: str = "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList/content"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def production_warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.app_env.lower() in {"prod", "production"}:
            if self.jwt_secret == "change-me-in-production":
                warnings.append("JWT_SECRET must be replaced with a managed secret")
            if not self.enable_api_key_auth:
                warnings.append("ENABLE_API_KEY_AUTH should be enabled or replaced by SSO/OIDC in production")
            if "fraud_password" in self.database_url:
                warnings.append("DATABASE_URL still contains the demo database password")
            if self.neo4j_password == "fraud_graph_password":
                warnings.append("NEO4J_PASSWORD still uses the demo graph password")
            if self.minio_secret_key == "fraudadmin123":
                warnings.append("MINIO_SECRET_KEY still uses the demo object-store password")
            if "*" in self.cors_origin_list:
                warnings.append("CORS origins must be pinned to trusted application origins")
        return warnings


@lru_cache
def get_settings() -> Settings:
    return Settings()
