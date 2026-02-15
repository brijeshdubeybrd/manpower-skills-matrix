from pydantic import BaseModel, ValidationError
from typing import List
import json

class EmployeeRecord(BaseModel):
    id: int
    Group: str
    SBU: str
    BU: str
    Function: str
    UJR_in_UJR_Master: str
    Job_Role_Name_without_concat: str
    L1_UJR: str
    Competency_Type: str
    Skill_Name: str
    Skill_Definition: str
    Proficiency_Level: int
    Band: str

try:
    with open("mock_db.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} records.")
    
    for i, record in enumerate(data):
        try:
            EmployeeRecord(**record)
        except ValidationError as e:
            print(f"Validation Error at index {i} (id={record.get('id')}):")
            print(e)
            break
            
    print("Validation detailed check complete.")

except Exception as e:
    print(f"Global Error: {e}")
