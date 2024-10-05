from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from models.user import User
from models.appointment import Appointment
from models.nutritional_plan import NutritionalPlan
from models.document import Document
from schemas.patient import PatientCreate, PatientUpdate, PatientOut
from schemas.appointment import AppointmentCreate, AppointmentOut
from schemas.nutritional_plan import NutritionalPlanCreate, NutritionalPlanOut
from schemas.document import DocumentCreate, DocumentOut
from routers.auth import get_current_user

router = APIRouter()

@router.post("/patients", response_model=PatientOut)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to create patients")
    
    new_patient = User(**patient.dict(), role="patient")
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/patients", response_model=List[PatientOut])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view all patients")
    patients = db.query(User).filter(User.role == "patient").offset(skip).limit(limit).all()
    return patients

@router.get("/patients/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role not in ["doctor", "admin"] and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this patient's information")
    return patient

@router.put("/patients/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role not in ["doctor", "admin"] and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this patient's information")
    
    for key, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete patients")
    
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient)
    db.commit()
    return None

@router.post("/patients/{patient_id}/appointments", response_model=AppointmentOut)
async def create_appointment(
    patient_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role not in ["doctor", "admin"] and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to create appointments for this patient")
    
    new_appointment = Appointment(**appointment.dict(), patient_id=patient_id)
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@router.get("/patients/{patient_id}/appointments", response_model=List[AppointmentOut])
async def get_patient_appointments(
    patient_id: int,
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role not in ["doctor", "admin"] and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this patient's appointments")
    
    query = db.query(Appointment).filter(Appointment.patient_id == patient_id)
    if start_date:
        query = query.filter(Appointment.date >= start_date)
    if end_date:
        query = query.filter(Appointment.date <= end_date)
    
    appointments = query.all()
    return appointments

@router.post("/patients/{patient_id}/nutritional-plans", response_model=NutritionalPlanOut)
async def create_nutritional_plan(
    patient_id: int,
    plan: NutritionalPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create nutritional plans")
    
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    new_plan = NutritionalPlan(**plan.dict(), patient_id=patient_id, doctor_id=current_user.id)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@router.get("/patients/{patient_id}/nutritional-plans", response_model=List[NutritionalPlanOut])
async def get_patient_nutritional_plans(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role not in ["doctor", "admin"] and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this patient's nutritional plans")
    
    plans = db.query(NutritionalPlan).filter(NutritionalPlan.patient_id == patient_id).all()
    return plans

@router.post("/patients/{patient_id}/documents", response_model=DocumentOut)
async def upload_patient_document(
    patient_id: int,
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role not in ["doctor", "admin"] and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to upload documents for this patient")
    
    new_document = Document(**document.dict(), user_id=patient_id)
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document

@router.get("/patients/{patient_id}/documents", response_model=List[DocumentOut])
async def get_patient_documents(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if current_user.role not in ["doctor", "admin"] and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this patient's documents")
    
    documents = db.query(Document).filter(Document.user_id == patient_id, Document.is_deleted == False).all()
    return documents