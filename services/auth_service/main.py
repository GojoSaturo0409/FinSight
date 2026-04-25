from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.auth_service.auth.router import router
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup (with retry for slow Postgres boot)
    from services.shared.database import create_tables
    for attempt in range(10):
        try:
            create_tables()
            break
        except Exception:
            time.sleep(2)
    yield

app = FastAPI(title="Auth Service", lifespan=lifespan)
app.include_router(router, prefix="/auth")
