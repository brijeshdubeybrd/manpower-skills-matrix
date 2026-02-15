from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from routers import pdf_export

app = FastAPI()

app.include_router(pdf_export.router, prefix="/api", tags=["export"])

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

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
 
# Helper to load/save DB
DB_FILE = "mock_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def read_root():
    return {"message": "Manpower & Skills Matrix API is running (JSON Mode)"}

@app.get("/api/manpower", response_model=List[EmployeeRecord])
def get_manpower_data():
    try:
        print("Loading DB...", flush=True)
        data = load_db()
        print(f"Loaded {len(data)} records. First record: {data[0] if data else 'None'}", flush=True)
        return data
    except Exception as e:
        print(f"ERROR in get_manpower_data: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise e

@app.post("/api/login")
def login(request: LoginRequest):
    print(f"Login attempt: {request.email} / {request.password}") # Debug log
    
    # Specific user credentials
    if request.email == "brijesh.dubey@raymond.in" and request.password == "pass123":
        return {"message": "OTP sent to " + request.email}
    
    # Test user
    if request.email == "demo@example.com" and request.password == "password":
         return {"message": "OTP sent to " + request.email}

    if request.email == "admin@raymond.in" and request.password == "@Pass123":
         return {"message": "OTP sent to " + request.email}

    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/verify-otp", response_model=TokenResponse)
def verify_otp(request: VerifyOtpRequest):
    if request.otp == "123456":
        return {"access_token": "mock-jwt-token-xyz-123", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/api/reset-data")
def reset_data():
    # In a real scenario, this would restore from a backup.
    # For now, we'll just re-run the generation script logic if needed, 
    # OR you can keep a "mock_db_original.json" to copy from.
    # Here we will just keep the current state or implement regeneration if strictly needed.
    # For simplicity in this JSON refactor, let's assume reset is a "no-op" or re-load 
    # unless we want to regenerate. Let's regenerate to be safe.
    import generate_json
    generate_json.generate_mock_data(60) # Re-run generation
    # We need to reload the modules or just re-run the script logic. 
    # Since generate_json is a script, we can run it via os.system or import function.
    # Let's use the subprocess or just write the file again.
    
    # Re-writing default data
    from generate_json import generate_mock_data
    data = generate_mock_data(60)
    save_db(data)
    
    return {"message": "Data reset successfully"}

@app.put("/api/manpower/{record_id}")
def update_record(record_id: int, updated_record: EmployeeRecord):
    db = load_db()
    for i, record in enumerate(db):
        if record["id"] == record_id:
            db[i] = updated_record.dict()
            save_db(db)
            return db[i]
    raise HTTPException(status_code=404, detail="Record not found")

@app.delete("/api/manpower/{record_id}")
def delete_record(record_id: int):
    db = load_db()
    for i, record in enumerate(db):
        if record["id"] == record_id:
            del db[i]
            save_db(db)
            return {"message": "Record deleted"}
    raise HTTPException(status_code=404, detail="Record not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
