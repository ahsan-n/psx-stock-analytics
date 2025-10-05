from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.api.v1 import auth, financial_data, reports

# Create database tables
base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PSX Stock Analytics API",
    description="AI-powered stock analytics for Pakistan Stock Exchange",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(financial_data.router, prefix="/api/v1/financial", tags=["Financial Data"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/")
async def root():
    return {
        "message": "PSX Stock Analytics API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
