from fastapi import FastAPI
from services.budget_service.budget.router import router
import threading
from services.budget_service.budget.subscriber import start_subscriber

app = FastAPI(title="Budget Service")
app.include_router(router, prefix="/budget")

@app.on_event("startup")
def startup_event():
    # Start the RabbitMQ pub-sub listener in a background daemon thread
    thread = threading.Thread(target=start_subscriber, daemon=True)
    thread.start()
