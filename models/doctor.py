from sqlalchemy import Column, Integer, String
from .common import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialization = Column(String)
    email = Column(String, unique=True, index=True)
    