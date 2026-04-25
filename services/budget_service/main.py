from fastapi import FastAPI
from services.budget_service.budget.router import router
app = FastAPI(title="Budget Service")
app.include_router(router, prefix="/budget")
