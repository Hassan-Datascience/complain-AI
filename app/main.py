from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import complaints_router, admin_router, analytics_router, auth_router
from app.services.database_manager import DatabaseManager

SEED_DEPARTMENTS = [
    {"department_id": "DEPT-ROAD", "name": "Roads Department", "category_handled": "Road"},
    {"department_id": "DEPT-WATER", "name": "Water Board", "category_handled": "Water/Drainage"},
    {"department_id": "DEPT-WASTE", "name": "Sanitation Department", "category_handled": "Waste"},
    {"department_id": "DEPT-ELEC", "name": "Power Department", "category_handled": "Electricity"},
    {"department_id": "DEPT-SAFE", "name": "Public Safety Department", "category_handled": "Safety"},
    {"department_id": "DEPT-GEN", "name": "General Services Department", "category_handled": "Other"},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup: Seed department mappings into database
    db = DatabaseManager()
    db.seed_departments(SEED_DEPARTMENTS)
    yield
    # Cleanup on shutdown (if any)

from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="AI Smart Civic Services API",
    description="End-to-End Backend for Civic Complaint Analysis, Prioritization & Analytics",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend or API consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(admin_router)
app.include_router(analytics_router)


# Mount frontend UI
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "AI Smart Civic Services API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "ui_url": "/ui/"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

