from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.user import UserOut
from routers.auth import get_current_user

router = APIRouter()

@router.get("/doctors", response_model=List[UserOut])
async def get_all_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctors = db.query(User).filter(User.role == "doctor").all()
    return doctors

@router.get("/doctors/{doctor_id}", response_model=UserOut)
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# Additional doctor-related endpoints can be added here
