from fastapi import APIRouter
from app.services.groq_service import groq_chat

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

@router.post("/ask")
async def ask_ai(payload: dict):
    question = payload.get("question", "")
    answer = groq_chat(question)
    return {"answer": answer}