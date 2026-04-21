from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the backend dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.router import router as ingestion_router
from categorization.router import router as categorization_router
from budget.router import router as budget_router
from recommendations.router import router as recommendations_router
from reports.router import router as reports_router
from auth.router import router as auth_router
from investments.router import router as investments_router

app = FastAPI(title="FinSight API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router, prefix="/ingestion", tags=["Ingestion"])
app.include_router(categorization_router, prefix="/categorization", tags=["Categorization"])
app.include_router(budget_router, prefix="/budget", tags=["Budget"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(investments_router, prefix="/investments", tags=["Investments"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FinSight API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
