from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.db.seed import seed_database
from app.api.v1 import (
    auth,
    dashboard,
    targets,
    discovery,
    inventory,
    scans,
    vulnerabilities,
    agents,
    reports,
    audit,
    staging_app
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed default roles, targets, and users
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
# SecuReX Backend API
Autonomous AI-Powered Real-Time Dynamic Application Security Testing (DAST) Platform.
Built for TBO VOYAGEHACK 4.0.

### Features:
- **10 Autonomous Agents**: Change Detection, Recon Discovery, Inventory Classification, Attack Planning, 5-Agent Testing Suite, Safety & Policy, Verification, Risk Assessment, Reporting, and Retesting.
- **Enterprise RBAC**: Roles for Admin, Security Engineer, Auditor, and Staging Agency Admin.
- **Synthetic Staging Testbed**: Travel booking API with configurable vulnerability flags for safe demonstration.
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(targets.router, prefix=settings.API_V1_STR)
app.include_router(discovery.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(scans.router, prefix=settings.API_V1_STR)
app.include_router(vulnerabilities.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(staging_app.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SecuReX Real-Time DAST Engine",
        "version": settings.PROJECT_VERSION
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to SecuReX - Autonomous Real-Time DAST Platform",
        "docs": "/docs",
        "status": "operational"
    }

