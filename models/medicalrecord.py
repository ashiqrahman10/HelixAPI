from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .common import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), index=True)
    date = Column(DateTime, index=True)
    diagnosis = Column(String)
    treatment = Column(String)
    notes = Column(String)
