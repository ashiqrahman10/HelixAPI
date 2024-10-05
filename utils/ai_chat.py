from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, ChatMessage
from pydantic import BaseModel
from typing import List
from datetime import datetime
import json
from groq import Groq
from ..config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    message: str
    timestamp: datetime

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(chat_request: ChatRequest, db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(User).filter(User.id == chat_request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate AI response using Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant for a healthcare application. Provide concise and informative responses."
            },
            {
                "role": "user",
                "content": chat_request.message
            }
        ],
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        stream=False,
        stop=None,
    )

    ai_response = completion.choices[0].message.content

    # Save the chat message to the database
    new_message = ChatMessage(
        user_id=chat_request.user_id,
        message=chat_request.message,
        response=ai_response,
        timestamp=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return ChatResponse(message=ai_response, timestamp=new_message.timestamp)

@router.get("/chat-history/{user_id}", response_model=List[ChatResponse])
async def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat_history = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    
    return [ChatResponse(message=chat.response, timestamp=chat.timestamp) for chat in chat_history]
