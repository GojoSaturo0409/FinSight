from fastapi import FastAPI
from services.analytics_service.recommendations.router import router as rec_router
from services.analytics_service.reports.router import router as rep_router
from services.analytics_service.investments.router import router as inv_router
app = FastAPI(title="Analytics Service")
app.include_router(rec_router, prefix="/recommendations")
app.include_router(rep_router, prefix="/reports")
app.include_router(inv_router, prefix="/investments")
