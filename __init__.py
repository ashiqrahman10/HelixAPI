from .config import settings
from .database import Base, engine, SessionLocal, get_db
from . import models
from .utils import diet_plan_router, notifications_router, ai_chat_router
from .routers import doctor_router, patient_router, lab_router, system_router

__all__ = [
    "settings",
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "models",
    "diet_plan_router",
    "notifications_router",
    "ai_chat_router",
    "doctor_router",
    "patient_router",
    "lab_router",
    "system_router"
]

# Initialize the database
from .database.session import init_db

# You might want to call init_db() here if you want to ensure the database is initialized
# when the package is imported. However, be cautious about potential circular imports.
# init_db()

# Version of your application
__version__ = "1.0.0"

# You can add any other initialization code here
