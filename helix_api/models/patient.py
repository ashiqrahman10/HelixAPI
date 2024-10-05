
from sqlalchemy import Column, Integer, String, Date
from .common import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date_of_birth = Column(Date)
    email = Column(String, unique=True, index=True)
    medical_history = Column(String)