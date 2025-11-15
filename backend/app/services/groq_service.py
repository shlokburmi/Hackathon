# app/services/groq_service.py
import httpx
from app.config import settings

async def query_groq(prompt: str) -> dict:
    """
    Async API call to Groq endpoint (replace URL with your real endpoint).
    """
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()
