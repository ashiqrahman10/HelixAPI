from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db

app = FastAPI(title="Helix API", description=" Not just a regular API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(doctor_router, prefix="/doctors", tags=["Doctors"])
# app.include_router(patient_router, prefix="/patients", tags=["Patients"])
# app.include_router(lab_router, prefix="/labs", tags=["Labs"])
# app.include_router(system_router, prefix="/system", tags=["System"])


@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Helix API"}

