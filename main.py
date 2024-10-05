from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import (
    diet_plan_router,
    notifications_router,
    ai_chat_router,
    doctor_router,
    patient_router,
    lab_router,
    system_router
)
from .database import init_db

app = FastAPI(title="Helix API", description="Not just a regular API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(diet_plan_router, prefix="/diet-plan", tags=["Diet Plan"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(ai_chat_router, prefix="/ai-chat", tags=["AI Chat"])
app.include_router(doctor_router, prefix="/doctors", tags=["Doctors"])
app.include_router(patient_router, prefix="/patients", tags=["Patients"])
app.include_router(lab_router, prefix="/labs", tags=["Labs"])
app.include_router(system_router, prefix="/system", tags=["System"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Helix API"}

