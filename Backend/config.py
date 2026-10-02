from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic_settings import JsonConfigSettingsSource
import yaml
import sys
import logging

BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)

class AuthConfig(BaseModel):
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

class LLMConfig(BaseModel):
    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.2
    max_tokens: int = 1024
    timeout_seconds: int = 30

class EmbeddingConfig(BaseModel):
    provider: str = "huggingface"
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"

class RerankerConfig(BaseModel):
    model: str | None = None

class VectorstoreConfig(BaseModel):
    policy_path: str = "data/vectorstores/policy_store"
    precedent_path: str = "data/vectorstores/precedent_store"

class BusinessRules(BaseModel):
    auto_approval_max_amount: float = 5000.0
    high_complexity_score_threshold: float = 7.0

class BillingConfig(BaseModel):
    default_fee: float = 150.0
    no_code_allowed_ratio: float = 0.8
    fee_schedule: Dict[str, float] = {}

class SeverityConfig(BaseModel):
    base: float = 1.0
    amount_high: float = 10000.0
    amount_high_points: float = 4.0
    amount_mid: float = 3000.0
    amount_mid_points: float = 2.0
    per_diagnosis: float = 0.8
    diagnosis_cap: float = 3.0
    per_procedure: float = 0.7
    procedure_cap: float = 3.0

class DebateConfig(BaseModel):
    base: float = 0.40
    per_argument: float = 0.15
    per_evidence: float = 0.10
    cap: float = 0.95

class UploadsConfig(BaseModel):
    dir: str = "data/uploads"
    max_mb: int = 10
    allowed_types: List[str] = ["application/pdf", "image/jpeg", "image/png"]

class Settings(BaseSettings):
    project_name: str = "Claims Adjudication Platform"
    env: str = "development"
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:5173"]

    auth: AuthConfig = Field(default_factory=AuthConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    agents: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    embeddings: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)
    vectorstore: VectorstoreConfig = Field(default_factory=VectorstoreConfig)
    business_rules: BusinessRules = Field(default_factory=BusinessRules)
    billing: BillingConfig = Field(default_factory=BillingConfig)
    severity: SeverityConfig = Field(default_factory=SeverityConfig)
    debate: DebateConfig = Field(default_factory=DebateConfig)
    uploads: UploadsConfig = Field(default_factory=UploadsConfig)

    # Secrets
    SECRET_KEY: str
    GROQ_API_KEY: str = ""
    HF_TOKEN: str = ""
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    DATABASE_URL: str = ""

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        v = (v or "").strip()
        OLD_PLACEHOLDER = "super-secret-key-change-this-in-production"
        if not v or v == OLD_PLACEHOLDER:
            raise ValueError(
                "SECRET_KEY is required and cannot be empty or set to the default placeholder 'super-secret-key-change-this-in-production'."
            )
        return v
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            return f"sqlite:///{BASE_DIR / 'claims_adjudication.db'}"
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls, json_file=BASE_DIR / "config.json"),
        )

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Loads and returns the YAML config for a given agent directory."""
        yaml_path = BASE_DIR / "agents" / agent_name / "agent.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Agent YAML config not found at: {yaml_path}")
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            overrides = self.agents.get(agent_name, {})
            if overrides:
                for k, v in overrides.items():
                    data[k] = v
            return data

    @property
    def ALGORITHM(self) -> str:
        return self.auth.algorithm
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.auth.access_token_expire_minutes

    @property
    def AUTO_APPROVAL_MAX_AMOUNT(self) -> float:
        return self.business_rules.auto_approval_max_amount
    
    @property
    def HIGH_COMPLEXITY_SCORE_THRESHOLD(self) -> float:
        return self.business_rules.high_complexity_score_threshold
    
    @property
    def LOG_LEVEL(self) -> str:
        return self.log_level
    
    @property
    def ENV(self) -> str:
        return self.env
    
    @property
    def PROJECT_NAME(self) -> str:
        return self.project_name
    
    @property
    def POLICY_VECTORSTORE_PATH(self) -> str:
        return str(BASE_DIR / self.vectorstore.policy_path)
    
    @property
    def PRECEDENT_VECTORSTORE_PATH(self) -> str:
        return str(BASE_DIR / self.vectorstore.precedent_path)

if not (BASE_DIR / "config.json").exists():
    print("Failed to start: config.json is missing", file=sys.stderr)
    sys.exit(1)

try:
    settings = Settings()
except Exception as e:
    print(f"Failed to load config.json: {e}", file=sys.stderr)
    sys.exit(1)

if not settings.GROQ_API_KEY:
    logger.warning("GROQ_API_KEY is not configured")
