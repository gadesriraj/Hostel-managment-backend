from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base, SessionLocal
from backend.routers import (
    auth_router,
    students_router,
    rooms_router,
    allocations_router,
    complaints_router,
    visitors_router,
    notices_router,
    feedback_router,
    analytics_router,
)
from backend.utils.seed_data import seed_database

# Create tables
Base.metadata.create_all(bind=engine)

# Seed initial data if tables are empty
with SessionLocal() as db:
    try:
        seed_database(db)
    except Exception as e:
        print(f"Seed note: {e}")

app = FastAPI(
    title="HostelSync REST API",
    description="Centralized Digital Hostel Management Platform API for Colleges & Universities",
    version="1.0.0",
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(rooms_router)
app.include_router(allocations_router)
app.include_router(complaints_router)
app.include_router(visitors_router)
app.include_router(notices_router)
app.include_router(feedback_router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {
        "message": "HostelSync API is operational",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
