# Event-Driven Architecture Migration Walkthrough

This document serves as proof of work for the successful migration of FinSight to a Pragmatic Event-Driven Architecture using RabbitMQ.

## 1. What Was Done
### Phase 1: Pub-Sub Foundation
Replaced the synchronous Observer pattern in the [BudgetMonitor](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/budget/monitor.py#10-108) with an asynchronous Pub-Sub approach using RabbitMQ. When budgets evaluate over threshold, the monitor now publishes a `BudgetThresholdExceeded` event to the `budget_events` fanout exchange. A background daemon subscriber processes these messages and notifies via [observers.py](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/budget/observers.py).

### Phase 2: Decoupling the Monolith
Successfully decoupled the ingestion routing logic from the core monolith into two distinct microservices while preserving the shared PostgreSQL state.
- **Service A (mine-ingestion-1)**: New FastAPI app running on port 8001. Handles all `/ingestion` endpoints. When a new transaction is saved to the database, an event publisher [publish_transaction_ingested(db_tx)](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/ingestion/events.py#7-34) publishes a `TransactionIngested` event to the `transaction_events` fanout exchange using Pika.
- **Service B (mine-backend-1)**: Core logic app running on port 8000. Features a new global RabbitMQ consumer that listens for `TransactionIngested`. Upon receiving an ingestion event, it evaluates Categorization Strategies and fires the Budget Monitor evaluators asynchronously.

## 2. Validation Results
Automated and manual tests were performed as detailed in the Verification Plan.

### Unit & Integration Verification
Unit tests via `python3 tests.py` successfully confirm the new architecture logic without breaking existing functionality. Pika connections were securely mocked. All logic tests (Observer triggers, Strategies, CoR, Auth) pass successfully with Exit Code 0.

### Docker Ecology
`docker compose up --build -d` correctly brings up the infrastructure. `mine-ingestion-1` maps port 8001, `mine-backend-1` maps port 8000. `rabbitmq` runs alongside them seamlessly.

### End-to-End Event Tracing
An automated test script was created and fired against the new microservices:
1. [test_e2e.py](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/test_e2e.py) authenticated sequentially against `mine-backend-1` to obtain a JWT.
2. The script triggered an HTTP POST to `http://localhost:8001/ingestion/manual` targeting `mine-ingestion-1`.
3. The logs from `mine-backend-1` confirmed the end-to-end receipt of the event:
```
backend-1  | 📱 [InAppNotifier] Budget WARNING: Food: You've spent $5955.50 in Food (limit: $500.00)
backend-1  | 📝 [LoggingObserver] AUDIT: level=warning | category=Food | spend=5955.50 | limit=500.00 | overage=5455.50
```
This proves all message flows operate accurately, decoupled cleanly via RabbitMQ Pub-Sub.

### Automated Visual Verification (Subagent)
An automated browser subagent executed a live UI test, authenticating against the frontend (running on `http://localhost:5173/`).
- The subagent verified that the **Dashboard Analytics** accurately aggregates total budget data directly from the processed RabbitMQ events.
- To facilitate dual-microservices, [apiFetch](file:///home/ayush/Sem8/SE/Project/P3/mine/frontend/src/api.ts#4-31) in [frontend/src/api.ts](file:///home/ayush/Sem8/SE/Project/P3/mine/frontend/src/api.ts) was patched successfully dynamically routing `/ingestion/*` endpoints to `--port 8001` and retaining everything else on `--port 8000`.

**Dashboard Verification Screenshot:**
![Analytics Insights Proof](/home/ayush/.gemini/antigravity/brain/c9c357ca-009b-45f4-97fc-87697597a944/analytics_insights_proof_1777049043623.png)

**Subagent Automation Recording:**
![Subagent Trace](/home/ayush/.gemini/antigravity/brain/c9c357ca-009b-45f4-97fc-87697597a944/finsight_frontend_e2e_test_1777048874021.webp)
