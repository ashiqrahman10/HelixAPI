from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, NutritionalPlan
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
from groq import Groq
from ..config import settings

router = APIRouter()

class DietPlanRequest(BaseModel):
    patient_id: int
    age: int
    weight: float
    existing_health_conditions: Optional[List[str]] = []
    goal: str
    dietary_preferences: str
    food_allergies_intolerances: Optional[List[str]] = []
    physical_activity_level: str

@router.post("/generate")
async def create_diet_plan(diet_plan: DietPlanRequest, db: Session = Depends(get_db)):
    # Check if the patient exists
    patient = db.query(User).filter(User.id == diet_plan.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Prepare data for AI model
    ai_input = diet_plan.model_dump()
    
    # Generate diet plan using Groq AI
    client = Groq(api_key=settings.GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": f"Generate a diet plan based on the following information: {json.dumps(ai_input)}\n\nGenerate diet plans based on health status, goals, and preferences and predict the impact of dietary changes on health outcomes. Return the response in a JSON format."
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    ai_response = completion.choices[0].message.content
    diet_plan_details = json.loads(ai_response)

    # Create a new NutritionalPlan entry in the database
    new_plan = NutritionalPlan(
        patient_id=diet_plan.patient_id,
        doctor_id=1,  # Assuming a default doctor ID for now. You might want to get this from the authenticated user or request.
        plan_details=json.dumps(diet_plan_details),
        start_date=datetime.now().date(),
        goals=diet_plan.goal,
        notes=f"Generated based on patient data: Age {diet_plan.age}, Weight {diet_plan.weight}, Activity Level {diet_plan.physical_activity_level}"
    )

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return {
        "message": "Diet plan created successfully",
        "plan_id": new_plan.id,
        "diet_plan": diet_plan_details
    }

@router.get("/patient/{patient_id}")
async def get_patient_diet_plans(patient_id: int, db: Session = Depends(get_db)):
    plans = db.query(NutritionalPlan).filter(NutritionalPlan.patient_id == patient_id).all()
    if not plans:
        raise HTTPException(status_code=404, detail="No diet plans found for this patient")
    
    return [
        {
            "id": plan.id,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "goals": plan.goals,
            "plan_details": json.loads(plan.plan_details)
        }
        for plan in plans
    ]

@router.get("/{plan_id}")
async def get_diet_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(NutritionalPlan).filter(NutritionalPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Diet plan not found")
    
    return {
        "id": plan.id,
        "patient_id": plan.patient_id,
        "doctor_id": plan.doctor_id,
        "start_date": plan.start_date,
        "end_date": plan.end_date,
        "goals": plan.goals,
        "plan_details": json.loads(plan.plan_details),
        "notes": plan.notes
    }
