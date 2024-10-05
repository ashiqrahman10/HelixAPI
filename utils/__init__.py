from .diet_plan import router as diet_plan_router
from .notifications import router as notifications_router
from .ai_chat import router as ai_chat_router

__all__ = ["diet_plan_router", "notifications_router", "ai_chat_router"]
