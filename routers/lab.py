from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.lab import LabTest
from schemas.user import UserOut
from schemas.lab import LabTestCreate, LabTestOut
from routers.auth import get_current_user

router = APIRouter()

@router.post("/lab-tests", response_model=LabTestOut)
async def create_lab_test(
    lab_test: LabTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create lab tests")
    
    new_lab_test = LabTest(**lab_test.dict())
    db.add(new_lab_test)
    db.commit()
    db.refresh(new_lab_test)
    return new_lab_test

@router.get("/lab-tests", response_model=List[LabTestOut])
async def get_lab_tests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lab_tests = db.query(LabTest).all()
    return lab_tests

@router.get("/lab-tests/{lab_test_id}", response_model=LabTestOut)
async def get_lab_test(
    lab_test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lab_test = db.query(LabTest).filter(LabTest.id == lab_test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    return lab_test

@router.put("/lab-tests/{lab_test_id}", response_model=LabTestOut)
async def update_lab_test(
    lab_test_id: int,
    lab_test_update: LabTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can update lab tests")
    
    db_lab_test = db.query(LabTest).filter(LabTest.id == lab_test_id).first()
    if not db_lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    
    for key, value in lab_test_update.dict().items():
        setattr(db_lab_test, key, value)
    
    db.commit()
    db.refresh(db_lab_test)
    return db_lab_test

@router.delete("/lab-tests/{lab_test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lab_test(
    lab_test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can delete lab tests")
    
    db_lab_test = db.query(LabTest).filter(LabTest.id == lab_test_id).first()
    if not db_lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    
    db.delete(db_lab_test)
    db.commit()
    return None
