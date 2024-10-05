from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from .common import Base

class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    test_name = Column(String)
    test_date = Column(DateTime)
    result = Column(String)