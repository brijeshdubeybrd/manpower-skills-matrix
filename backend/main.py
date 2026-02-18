from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from routers import pdf_export
from db import bq_client

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
        print("Fetching data from BigQuery...", flush=True)
        data = bq_client.get_manpower_data()
        
        if not data:
             # Just log, but don't fallback. Return empty list if BQ is empty.
             print("BigQuery returned no data.", flush=True)
             return []

        print(f"Fetched {len(data)} records from BigQuery.", flush=True)
        return data
    except Exception as e:
        print(f"ERROR in get_manpower_data: {e}", flush=True)
        import traceback
        traceback.print_exc()
        # Raise 500 explicitly so user knows BQ failed
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from BigQuery: {str(e)}")

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
    # Data reset is disabled to preserve manual changes in mock_db.json
    return {"message": "Data reset is disabled to preserve manual changes."}

@app.put("/api/manpower/{record_id}")
def update_record(record_id: int, updated_record: EmployeeRecord):
    # Try BigQuery Update (Mock implementation for now)
    success = bq_client.update_record(record_id, updated_record.dict())
    if success:
         return updated_record
    
    # Fallback to local mock DB for editing
    print("Updating local mock DB as BigQuery update is not fully implemented.", flush=True)
    db = load_db()
    for i, record in enumerate(db):
        if record["id"] == record_id:
            db[i] = updated_record.dict()
            save_db(db)
            return db[i]
    raise HTTPException(status_code=404, detail="Record not found")

@app.delete("/api/manpower/{record_id}")
def delete_record(record_id: int):
    # Try BigQuery Delete
    success = bq_client.delete_record(record_id)
    if success:
        return {"message": "Record deleted from BigQuery"}

    # Fallback to local mock DB
    print("Deleting from local mock DB as BigQuery delete is not fully implemented.", flush=True)
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
