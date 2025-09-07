#!/usr/bin/env python3
"""
Stub API server that serves sample data from JSON for demonstration.
This bypasses database connection issues and provides working endpoints.
"""

import json
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel

app = FastAPI(title="MiraiWorks HRMS - Demo API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3004",
        "http://127.0.0.1:3004",
        "http://localhost:3005",
        "http://127.0.0.1:3005",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Load sample data
def load_sample_data():
    try:
        with open("sample_data.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "users": [],
            "companies": [],
            "jobs": [],
            "interviews": [],
            "messages": [],
            "meta": {},
        }


sample_data = load_sample_data()


# Pydantic models for responses
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: dict[str, Any]


class User(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    email_verified: bool
    company_id: Optional[int] = None


class Company(BaseModel):
    id: int
    name: str
    description: str
    website: str
    industry: str
    size_category: str
    location: str


class Job(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    company_id: int
    posted_by: int
    location: str
    employment_type: str
    salary_min: int
    salary_max: int
    salary_currency: str
    status: str
    created_at: str
    application_deadline: str


class Interview(BaseModel):
    id: int
    candidate_id: int
    recruiter_id: int
    title: str
    scheduled_at: str
    duration_minutes: int
    interview_type: str
    status: str
    meeting_link: str
    notes: str


class Message(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    subject: str
    content: str
    thread_id: str
    is_read: bool
    created_at: str


# Mock authentication
def get_current_user(token: str = Depends(security)):
    # In a real app, verify the JWT token
    # For demo, return the first admin user
    if sample_data["users"]:
        return sample_data["users"][0]
    raise HTTPException(status_code=401, detail="Invalid token")


# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "MiraiWorks HRMS API - Demo Mode",
        "version": "1.0.0",
        "status": "running",
        "demo_mode": True,
    }


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """Mock login endpoint"""
    # Find user by email
    user = next(
        (u for u in sample_data["users"] if u["email"] == login_request.email), None
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # For demo, accept any password
    return LoginResponse(
        access_token="demo_access_token_" + str(user["id"]),
        refresh_token="demo_refresh_token_" + str(user["id"]),
        expires_in=3600,
        user=user,
    )


@app.get("/api/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return User(**current_user)


@app.get("/api/users", response_model=list[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users"""
    return [User(**user) for user in sample_data["users"]]


@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get user by ID"""
    user = next((u for u in sample_data["users"] if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)


@app.get("/api/companies", response_model=list[Company])
async def get_companies(current_user: dict = Depends(get_current_user)):
    """Get all companies"""
    return [Company(**company) for company in sample_data["companies"]]


@app.get("/api/companies/{company_id}", response_model=Company)
async def get_company(company_id: int, current_user: dict = Depends(get_current_user)):
    """Get company by ID"""
    company = next((c for c in sample_data["companies"] if c["id"] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return Company(**company)


@app.get("/api/jobs", response_model=list[Job])
async def get_jobs(current_user: dict = Depends(get_current_user)):
    """Get all jobs"""
    return [Job(**job) for job in sample_data["jobs"]]


@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: int, current_user: dict = Depends(get_current_user)):
    """Get job by ID"""
    job = next((j for j in sample_data["jobs"] if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**job)


@app.get("/api/interviews", response_model=list[Interview])
async def get_interviews(current_user: dict = Depends(get_current_user)):
    """Get all interviews"""
    return [Interview(**interview) for interview in sample_data["interviews"]]


@app.get("/api/interviews/{interview_id}", response_model=Interview)
async def get_interview(
    interview_id: int, current_user: dict = Depends(get_current_user)
):
    """Get interview by ID"""
    interview = next(
        (i for i in sample_data["interviews"] if i["id"] == interview_id), None
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return Interview(**interview)


@app.get("/api/messages", response_model=list[Message])
async def get_messages(current_user: dict = Depends(get_current_user)):
    """Get all messages"""
    return [Message(**message) for message in sample_data["messages"]]


@app.get("/api/messages/{message_id}", response_model=Message)
async def get_message(message_id: int, current_user: dict = Depends(get_current_user)):
    """Get message by ID"""
    message = next((m for m in sample_data["messages"] if m["id"] == message_id), None)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return Message(**message)


@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    return {
        "total_users": len(sample_data["users"]),
        "total_companies": len(sample_data["companies"]),
        "total_jobs": len(sample_data["jobs"]),
        "total_interviews": len(sample_data["interviews"]),
        "total_messages": len(sample_data["messages"]),
        "active_jobs": len([j for j in sample_data["jobs"] if j["status"] == "active"]),
        "scheduled_interviews": len(
            [i for i in sample_data["interviews"] if i["status"] == "scheduled"]
        ),
        "unread_messages": len(
            [m for m in sample_data["messages"] if not m["is_read"]]
        ),
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting MiraiWorks HRMS Demo API...")
    print("Frontend should connect to http://localhost:8001")
    print("API docs available at http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
