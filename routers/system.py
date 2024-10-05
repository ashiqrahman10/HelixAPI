from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.prescription import Prescription
from schemas.user import UserOut, UserCreate, UserUpdate
from schemas.prescription import PrescriptionOut
from schemas.system import SystemStats
from routers.auth import get_current_user
from services.notification_service import send_medication_notification
from services.function_calling_service import execute_function

router = APIRouter()

@router.get("/system/users", response_model=List[UserOut])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all users")
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/system/user/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view user details")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/system/user", response_model=UserOut)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/system/user/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update users")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/system/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None

@router.post("/system/medication-notifications")
async def send_medication_notifications(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can trigger medication notifications")
    
    now = datetime.utcnow()
    upcoming_prescriptions = db.query(Prescription).filter(
        Prescription.start_date <= now,
        Prescription.end_date >= now
    ).all()
    
    for prescription in upcoming_prescriptions:
        background_tasks.add_task(send_medication_notification, prescription)
    
    return {"message": f"Medication notifications queued for {len(upcoming_prescriptions)} prescriptions"}

@router.post("/system/function-call")
async def function_call(
    function_name: str,
    parameters: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can use the function calling API")
    
    result = execute_function(function_name, parameters)
    return {"result": result}

@router.get("/system/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view system stats")
    
    total_users = db.query(User).count()
    total_patients = db.query(User).filter(User.role == "patient").count()
    total_doctors = db.query(User).filter(User.role == "doctor").count()
    total_prescriptions = db.query(Prescription).count()
    
    return SystemStats(
        total_users=total_users,
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_prescriptions=total_prescriptions
    )

@router.get("/system/health")
async def health_check():
    return {"status": "healthy"}