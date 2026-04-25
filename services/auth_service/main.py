from fastapi import FastAPI
from services.auth_service.auth.router import router
app = FastAPI(title="Auth Service")
app.include_router(router, prefix="/auth")
