from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from typing import List, Literal
import os

router = APIRouter()

# Instantiate the new OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4"
            messages=request.messages,
            temperature=0.5,
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"❌ Error: {str(e)}"}


