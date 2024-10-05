from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings
from sqlalchemy.orm import declarative_base

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    from ..models import User, DoctorProfile, LabTechnicianProfile, Appointment, Diagnosis, Prescription, Lab, LabEquipment, LabReport, Attendance, NutritionalPlan, Document
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    init_db()