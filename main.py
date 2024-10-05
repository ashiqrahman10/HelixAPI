from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from helix_api.routers import doctor, patient, lab, auth, system
from helix_api.database import init_db

app = FastAPI(title="Helix API", description="API for the Helix healthcare system", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(doctor.router, prefix="/doctors", tags=["Doctors"])
app.include_router(patient.router, prefix="/patients", tags=["Patients"])
app.include_router(lab.router, prefix="/labs", tags=["Labs"])
app.include_router(system.router, prefix="/system", tags=["System"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Helix API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
