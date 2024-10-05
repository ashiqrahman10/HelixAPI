from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Prescription
from pydantic import BaseModel
from typing import List
from datetime import datetime, date
from ..config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()

class MedicationReminder(BaseModel):
    patient_id: int
    medication: str
    dosage: str
    frequency: str

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.EMAIL_SENDER, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

@router.post("/send-medication-reminder")
async def send_medication_reminder(reminder: MedicationReminder, db: Session = Depends(get_db)):
    patient = db.query(User).filter(User.id == reminder.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    subject = "Medication Reminder"
    body = f"Reminder: It's time to take your {reminder.medication}. Dosage: {reminder.dosage}. Frequency: {reminder.frequency}"

    send_email(patient.email, subject, body)
    return {"message": "Medication reminder sent successfully"}

@router.post("/schedule-medication-reminders")
async def schedule_medication_reminders(db: Session = Depends(get_db)):
    today = date.today()
    active_prescriptions = db.query(Prescription).filter(
        Prescription.start_date <= today,
        Prescription.end_date >= today
    ).all()

    reminders_sent = 0
    for prescription in active_prescriptions:
        patient = db.query(User).filter(User.id == prescription.patient_id).first()
        if patient and patient.email:
            reminder = MedicationReminder(
                patient_id=patient.id,
                medication=prescription.medication,
                dosage=prescription.dosage,
                frequency=prescription.frequency
            )
            await send_medication_reminder(reminder, db)
            reminders_sent += 1

    return {"message": f"Scheduled {reminders_sent} medication reminders"}
