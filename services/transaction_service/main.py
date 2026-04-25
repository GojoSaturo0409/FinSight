from fastapi import FastAPI
from services.transaction_service.ingestion.router import router as ing_router
from services.transaction_service.categorization.router import router as cat_router
from services.transaction_service.currency_converter.router import router as cur_router
app = FastAPI(title="Transaction Service")
app.include_router(ing_router, prefix="/ingestion")
app.include_router(cat_router, prefix="/categorization")
app.include_router(cur_router, prefix="/currency")
