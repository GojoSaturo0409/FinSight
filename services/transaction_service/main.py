from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading

def run_subscriber():
    from services.shared.core.subscriber import start_core_subscriber
    start_core_subscriber()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the core subscriber in a background daemon thread
    thread = threading.Thread(target=run_subscriber, daemon=True)
    thread.start()
    yield

from services.transaction_service.ingestion.router import router as ing_router
from services.transaction_service.categorization.router import router as cat_router
from services.transaction_service.currency_converter.router import router as cur_router

app = FastAPI(title="Transaction Service", lifespan=lifespan)
app.include_router(ing_router, prefix="/ingestion")
app.include_router(cat_router, prefix="/categorization")
app.include_router(cur_router, prefix="/currency")
