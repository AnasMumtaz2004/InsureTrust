import os
import json
import pytest
from pathlib import Path

def test_config_json_loads():
    from config import Settings, LLMConfig
    settings = Settings()
    assert settings.project_name == "Claims Adjudication Platform"
    assert settings.llm.model == "llama-3.3-70b-versatile"
    assert settings.llm.provider == "groq"

def test_env_var_override(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    from config import Settings
    settings = Settings()
    assert settings.log_level == "DEBUG"
    assert settings.LOG_LEVEL == "DEBUG"

def test_startup_fails_empty_secret(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "")
    from config import Settings
    with pytest.raises(ValueError, match="SECRET_KEY is required"):
        Settings()
        
def test_startup_fails_old_placeholder_secret(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "super-secret-key-change-this-in-production")
    from config import Settings
    with pytest.raises(ValueError, match="SECRET_KEY is required"):
        Settings()

def test_config_json_no_secrets():
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "r") as f:
        data = json.load(f)
        
    import re
    secret_pattern = re.compile(r"(?i)(secret|password|api_key|token)")
    
    def walk_dict(d):
        for k, v in d.items():
            if secret_pattern.search(k) and k not in ["access_token_expire_minutes", "max_tokens"]:
                pytest.fail(f"Found secret-like key in config.json: {k}")
            if isinstance(v, dict):
                walk_dict(v)
                
    walk_dict(data)

def test_get_chat_llm_raises_without_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    from config import Settings
    
    import services.llm_service
    monkeypatch.setattr(services.llm_service, "settings", Settings(GROQ_API_KEY=""))
    
    with pytest.raises(RuntimeError, match="GROQ_API_KEY is not configured"):
        services.llm_service.get_chat_llm()

def test_get_chat_llm_uses_config(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    from config import Settings
    
    import services.llm_service
    monkeypatch.setattr(services.llm_service, "settings", Settings(GROQ_API_KEY="fake-key"))
    
    llm = services.llm_service.get_chat_llm()
    
    assert llm.model_name == "llama-3.3-70b-versatile"
    assert llm.temperature == 0.2
    assert llm.groq_api_key.get_secret_value() == "fake-key"
