import os
from pathlib import Path
from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Claims Adjudication Platform"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'claims_adjudication.db'}"

    # LLM Settings
    OPENAI_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "gpt-4o"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # RAG Vector Store Paths
    POLICY_VECTORSTORE_PATH: str = str(BASE_DIR / "data" / "vectorstores" / "policy_store")
    PRECEDENT_VECTORSTORE_PATH: str = str(BASE_DIR / "data" / "vectorstores" / "precedent_store")

    # Business Rules
    AUTO_APPROVAL_MAX_AMOUNT: float = 5000.00
    HIGH_COMPLEXITY_SCORE_THRESHOLD: float = 7.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Loads and returns the YAML config for a given agent directory."""
        yaml_path = BASE_DIR / "agents" / agent_name / "agent.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Agent YAML config not found at: {yaml_path}")
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

settings = Settings()
