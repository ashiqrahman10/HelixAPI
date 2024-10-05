from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from database import get_db
from models.user import User
from models.appointment import Appointment
from models.diagnosis import Diagnosis
from models.prescription import Prescription
from schemas.user import UserOut, UserCreate, UserUpdate
from schemas.appointment import AppointmentCreate, AppointmentOut
from schemas.diagnosis import DiagnosisCreate, DiagnosisOut
from schemas.prescription import PrescriptionCreate, PrescriptionOut
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

@router.post("/doctors", response_model=UserOut)
async def create_doctor(
    doctor: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create doctors")
    new_doctor = User(**doctor.dict(), role="doctor")
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

@router.put("/doctors/{doctor_id}", response_model=UserOut)
async def update_doctor(
    doctor_id: int,
    doctor_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this doctor")
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for key, value in doctor_update.dict(exclude_unset=True).items():
        setattr(doctor, key, value)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete doctors")
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
    return {"message": "Doctor deleted successfully"}

@router.post("/doctors/{doctor_id}/attendance", status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    doctor_id: int,
    attendance_date: date = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to mark attendance")
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    # Implement attendance marking logic here
    return {"message": f"Attendance marked for doctor {doctor_id} on {attendance_date}"}

@router.post("/doctors/{doctor_id}/diagnoses", response_model=DiagnosisOut)
async def create_diagnosis(
    doctor_id: int,
    diagnosis: DiagnosisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor" or current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to create diagnoses")
    new_diagnosis = Diagnosis(**diagnosis.dict(), doctor_id=doctor_id)
    db.add(new_diagnosis)
    db.commit()
    db.refresh(new_diagnosis)
    return new_diagnosis

@router.post("/doctors/{doctor_id}/prescriptions", response_model=PrescriptionOut)
async def create_prescription(
    doctor_id: int,
    prescription: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor" or current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to create prescriptions")
    new_prescription = Prescription(**prescription.dict(), doctor_id=doctor_id)
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription

@router.post("/doctors/{doctor_id}/appointments", response_model=AppointmentOut)
async def schedule_appointment(
    doctor_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    new_appointment = Appointment(**appointment.dict(), doctor_id=doctor_id)
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@router.get("/doctors/{doctor_id}/appointments", response_model=List[AppointmentOut])
async def get_doctor_appointments(
    doctor_id: int,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these appointments")
    query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
    if start_date:
        query = query.filter(Appointment.date >= start_date)
    if end_date:
        query = query.filter(Appointment.date <= end_date)
    appointments = query.all()
    return appointments