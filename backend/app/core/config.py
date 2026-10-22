"""Application configuration and environment settings."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Application Settings
    PROJECT_NAME: str = "Carrier-Grade Telecom Cloud RCA & SLA Liability Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

    # Integration Modes (Person C Isolation)
    USE_FIXTURES: bool = True  # True: use fixture-backed clients; False: call live Person A/B endpoints
    MOCK_BEDROCK: bool = True  # True: deterministic offline LLM reasoning; False: live AWS Bedrock Claude 3.5 Sonnet

    # Amazon Bedrock Settings
    AWS_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_TIMEOUT_SECONDS: int = 30
    BEDROCK_MAX_RETRIES: int = 3

    # AGORA Safety & Compliance Settings
    AGORA_WINDOW_SECONDS: float = 5.0  # State estimation required within last 5 seconds

    # HITL Cryptographic Governance Settings
    HITL_SECRET_KEY: str = "carrier-grade-hitl-hmac-secret-key-change-in-production-2026"
    HITL_TOKEN_EXPIRY_MINUTES: int = 60

    # LASM MRC Penalty Thresholds
    LASM_HIGH_PENALTY_THRESHOLD: float = 0.30  # trust < 0.30 -> 30% MRC penalty
    LASM_MED_PENALTY_THRESHOLD: float = 0.60   # 0.30 <= trust < 0.60 -> 20% MRC penalty
    LASM_LOW_PENALTY_THRESHOLD: float = 0.80   # 0.60 <= trust < 0.80 -> 10% MRC penalty

    # Paths
    KB_RULES_PATH: Path = BASE_DIR / "knowledge_base" / "failure_rules.yaml"
    FIXTURES_DIR: Path = BASE_DIR / "tests" / "fixtures"

    # Live Endpoints (for Week 11 Integration when USE_FIXTURES=false)
    PERSON_A_MCP_URL: Optional[str] = "http://mcp-telemetry.internal:8080"
    PERSON_B_RCA_URL: Optional[str] = "http://sagemaker-rca.internal:8000"
    VECTOR_DB_URL: Optional[str] = "postgresql://user:pass@localhost:5432/vectordb"


settings = Settings()
