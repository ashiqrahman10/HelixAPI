from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from models.user import User
from models.lab import Lab, LabEquipment, LabReport
from schemas.lab import (
    LabCreate, LabOut, 
    LabEquipmentCreate, LabEquipmentOut, LabEquipmentUpdate,
    LabReportCreate, LabReportOut, LabReportUpdate
)
from routers.auth import get_current_user

router = APIRouter()

# Lab routes
@router.post("/labs", response_model=LabOut)
async def create_lab(
    lab: LabCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create labs")
    new_lab = Lab(**lab.dict())
    db.add(new_lab)
    db.commit()
    db.refresh(new_lab)
    return new_lab

@router.get("/labs", response_model=List[LabOut])
async def get_labs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    labs = db.query(Lab).all()
    return labs

@router.get("/labs/{lab_id}", response_model=LabOut)
async def get_lab(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab

# Lab Equipment routes
@router.post("/labs/{lab_id}/equipment", response_model=LabEquipmentOut)
async def create_lab_equipment(
    lab_id: int,
    equipment: LabEquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "lab_technician"]:
        raise HTTPException(status_code=403, detail="Not authorized to create lab equipment")
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    new_equipment = LabEquipment(**equipment.dict(), lab_id=lab_id)
    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)
    return new_equipment

@router.get("/labs/{lab_id}/equipment", response_model=List[LabEquipmentOut])
async def get_lab_equipment(
    lab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    equipment = db.query(LabEquipment).filter(LabEquipment.lab_id == lab_id).all()
    return equipment

@router.put("/labs/{lab_id}/equipment/{equipment_id}", response_model=LabEquipmentOut)
async def update_lab_equipment(
    lab_id: int,
    equipment_id: int,
    equipment_update: LabEquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "lab_technician"]:
        raise HTTPException(status_code=403, detail="Not authorized to update lab equipment")
    equipment = db.query(LabEquipment).filter(LabEquipment.id == equipment_id, LabEquipment.lab_id == lab_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    for key, value in equipment_update.dict(exclude_unset=True).items():
        setattr(equipment, key, value)
    db.commit()
    db.refresh(equipment)
    return equipment

# Lab Report routes
@router.post("/lab-reports", response_model=LabReportOut)
async def create_lab_report(
    report: LabReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["doctor", "lab_technician"]:
        raise HTTPException(status_code=403, detail="Not authorized to create lab reports")
    new_report = LabReport(**report.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/lab-reports", response_model=List[LabReportOut])
async def get_lab_reports(
    patient_id: int = None,
    doctor_id: int = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(LabReport)
    if patient_id:
        query = query.filter(LabReport.patient_id == patient_id)
    if doctor_id:
        query = query.filter(LabReport.doctor_id == doctor_id)
    if start_date:
        query = query.filter(LabReport.test_date >= start_date)
    if end_date:
        query = query.filter(LabReport.test_date <= end_date)
    reports = query.all()
    return reports

@router.get("/lab-reports/{report_id}", response_model=LabReportOut)
async def get_lab_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    return report

@router.put("/lab-reports/{report_id}", response_model=LabReportOut)
async def update_lab_report(
    report_id: int,
    report_update: LabReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["doctor", "lab_technician"]:
        raise HTTPException(status_code=403, detail="Not authorized to update lab reports")
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    for key, value in report_update.dict(exclude_unset=True).items():
        setattr(report, key, value)
    db.commit()
    db.refresh(report)
    return report

@router.delete("/lab-reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lab_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete lab reports")
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    db.delete(report)
    db.commit()
    return None