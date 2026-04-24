from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.router import router as ingestion_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import create_tables
    create_tables()
    yield

app = FastAPI(title="FinSight Ingestion API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router, prefix="/ingestion", tags=["Ingestion"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ingestion"}
