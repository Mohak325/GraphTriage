"""Application configuration and environment settings using Pydantic Settings."""

from functools import lru_cache
from typing import List, Tuple, Union
import logging
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for GraphTriage Backend."""

    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Bind host")
    PORT: int = Field(default=8000, description="Bind port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    APP_NAME: str = "GraphTriage API"
    APP_VERSION: str = "0.1.0"

    # CORS settings
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )

    # Neo4j Graph Database
    NEO4J_URI: str = Field(default="bolt://localhost:7687", description="Neo4j Bolt connection URI")
    NEO4J_USER: str = Field(default="neo4j", description="Neo4j username")
    NEO4J_PASSWORD: str = Field(default="graphtriage_dev", description="Neo4j password")
    NEO4J_AUTH: str = Field(default="", description="Optional neo4j user/password combined string")
    NEO4J_DATABASE: str = Field(default="neo4j", description="Default database name")
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=50, description="Max connection pool size")
    NEO4J_CONNECTION_TIMEOUT: float = Field(default=30.0, description="Connection timeout in seconds")

    # Redis (Celery broker + event cache)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # AI / LLM Integration
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key for agent verification")

    # RCA Algorithm Parameters
    FAULT_GRADIENT_ALPHA: float = Field(default=0.85, description="Diffusion damping factor (alpha)")
    FAULT_GRADIENT_EPSILON: float = Field(default=1e-6, description="Convergence tolerance")
    FAULT_GRADIENT_MAX_ITER: int = Field(default=100, description="Max power iteration steps")

    model_config = SettingsConfigDict(
        env_file=(".env", "docker/.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def neo4j_auth_credentials(self) -> Tuple[str, str]:
        """Resolves (user, password) handling both separate vars and NEO4J_AUTH string."""
        if self.NEO4J_AUTH and "/" in self.NEO4J_AUTH:
            parts = self.NEO4J_AUTH.split("/", 1)
            return parts[0], parts[1]
        return self.NEO4J_USER, self.NEO4J_PASSWORD


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
