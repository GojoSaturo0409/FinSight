from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Ensure services directory is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.auth_service.auth.router import router as auth_router
from services.transaction_service.ingestion.router import router as ingestion_router
from services.transaction_service.categorization.router import router as categorization_router
from services.transaction_service.currency_converter.router import router as currency_router
from services.budget_service.budget.router import router as budget_router
from services.analytics_service.recommendations.router import router as recommendations_router
from services.analytics_service.reports.router import router as reports_router
from services.analytics_service.investments.router import router as investments_router

app = FastAPI(title="FinSight API Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(ingestion_router, prefix="/ingestion", tags=["Ingestion"])
app.include_router(categorization_router, prefix="/categorization", tags=["Categorization"])
app.include_router(currency_router, prefix="/currency", tags=["Currency"])
app.include_router(budget_router, prefix="/budget", tags=["Budget"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(investments_router, prefix="/investments", tags=["Investments"])

@app.get("/")
def read_root():
    return {"message": "FinSight API Gateway Active"}
