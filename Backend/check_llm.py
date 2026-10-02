import traceback
from config import settings

print("key loaded:", bool(settings.GROQ_API_KEY), "| key length:", len(settings.GROQ_API_KEY))
try:
    print("model:", settings.llm.model)
    from services.llm_service import get_chat_llm
    print("reply:", get_chat_llm().invoke("Say hi in 3 words").content)
except Exception:
    traceback.print_exc()
