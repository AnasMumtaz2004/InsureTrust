from langchain_groq import ChatGroq
from config import settings

def get_chat_llm(agent_name: str | None = None) -> ChatGroq:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    
    model = settings.llm.model
    temperature = settings.llm.temperature
    max_tokens = settings.llm.max_tokens
    timeout = settings.llm.timeout_seconds

    if agent_name and agent_name in settings.agents:
        agent_overrides = settings.agents[agent_name]
        model = agent_overrides.get("model", model)
        temperature = agent_overrides.get("temperature", temperature)
        max_tokens = agent_overrides.get("max_tokens", max_tokens)
        timeout = agent_overrides.get("timeout_seconds", timeout)

    return ChatGroq(
        model=model,
        groq_api_key=settings.GROQ_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout
    )
