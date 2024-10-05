from pydantic import BaseModel, EmailStr

class DoctorBase(BaseModel):
    name: str
    specialization: str
    email: EmailStr

class DoctorCreate(DoctorBase):
    password: str

class DoctorUpdate(DoctorBase):
    pass

class DoctorOut(DoctorBase):
    id: int

    class Config:
        orm_mode = True


class Doctor(DoctorBase):
    id: int

    class Config:
        orm_mode = True