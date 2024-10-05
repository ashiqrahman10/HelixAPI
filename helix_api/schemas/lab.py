from pydantic import BaseModel
from datetime import datetime

class LabTestBase(BaseModel):
    patient_id: int
    test_name: str
    test_date: datetime
    result: str = None

class LabTestCreate(LabTestBase):
    pass

class LabTestUpdate(LabTestBase):
    pass

class LabTest(LabTestBase):
    id: int

    class Config:
        orm_mode = True