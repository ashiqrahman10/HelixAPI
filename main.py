from typing import Union, List, Optional
from groq import Groq
from fastapi import FastAPI
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()  # Load environment variables from the .env file

app = FastAPI()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Define a Pydantic model for the request body
class DietPlanRequest(BaseModel):
    age: int
    weight: float
    existing_health_conditions: Optional[List[str]] = []
    goal: str
    dietary_preferences: str
    food_allergies_intolerances: Optional[List[str]] = []
    physical_activity_level: str

@app.post("/diet-plan")
async def generate_diet_plan(request_data: DietPlanRequest):
    json_data = request_data.json()
    print(json_data)


    client = Groq()
    completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "user",
            "content": "I will give you a JSON with the following data of a person \"Age\nWeight\nExisting Health Conditions\nGoal\nDietary Preferences\nFood Allergies/Intolerances\nPhysical Activity Level\"\n\nyou are to generate a Generate diet plans based on health status, goals, and preferences and Predict the impact of dietary changes on health outcomes.\nreturn the response in a JSON"
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    response_format={"type": "json_object"},
    stop=None,
    )

    response = completion.choices[0].message.content
    response_json = json.loads(response)
    return response_json