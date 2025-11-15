# app/routers/ai.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.groq_service import query_groq
from app.security import get_current_user


router = APIRouter(prefix="/ai", tags=["AI"])

class AIPrompt(BaseModel):
    prompt: str

@router.post("/query")
async def ai_query(payload: AIPrompt, current_user: dict = Depends(get_current_user)):
    try:
        res = await query_groq(payload.prompt)
        return {"ok": True, "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
