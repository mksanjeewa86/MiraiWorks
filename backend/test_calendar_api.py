#!/usr/bin/env python3
"""
Test script for calendar API endpoints without database dependency.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import just the calendar router
from app.endpoints.calendar import router as calendar_router

# Create minimal FastAPI app
app = FastAPI(title="Calendar API Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only calendar router
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])

@app.get("/")
async def root():
    return {"message": "Calendar API Test Server"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)