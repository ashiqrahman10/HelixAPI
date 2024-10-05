from pydantic import BaseModel, EmailStr
from datetime import date

class PatientBase(BaseModel):
    name: str
    date_of_birth: date
    email: EmailStr
    medical_history: str = None

class PatientCreate(PatientBase):
    password: str

class PatientUpdate(PatientBase):
    pass

class PatientOut(PatientBase):
    id: int

    class Config:
        orm_mode = True


class Patient(PatientBase):
    id: int

    class Config:
        orm_mode = True