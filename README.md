# FinSight

FinSight is a personal finance management platform offering multi-source transaction ingestion, real-time budget tracking, and an analytics dashboard with a savings recommendation engine.

## Project Architecture

This prototype utilizes a Three-Tier architecture designed with modern aesthetics and strict decoupling facilitated via fundamental software engineering Design Patterns.

### Frontend
- **Framework:** React 18 (Vite)
- **Styling:** Tailwind CSS v4 (Glassmorphic Interface)
- **Visualizations:** Chart.js

### Backend (Microservices Core)
- **Architecture:** Distributed Microservices (`api_gateway`, `auth_service`, `transaction_service`, `budget_service`, `analytics_service`)
- **Frameworks:** FastAPI, Nginx (Gateway)
- **Database:** PostgreSQL 15 via SQLAlchemy
- **Messaging/Async:** RabbitMQ & Celery
- **Caching:** Redis

### Implemented Design Patterns
1. **Factory Pattern:** `TransactionFactory` evaluates data sources (e.g. Plaid, CSV) to generate correct parsing instances.
2. **Adapter Pattern:** `PlaidAdapter` and `CSVAdapter` conform unstructured external data to a common domain `Transaction` model.
3. **Chain of Responsibility Pattern:** 
   - Used in the Recommendation Engine to funnel data sequentially through handlers (`HighSpendDetector`, `SubscriptionAuditHandler`).
   - Used for Currency Conversion failover mechanisms across APIs and DB Cache fallbacks.
4. **Strategy Pattern:** `CategorizationService` allows switching logic implementations between algorithm modes (`RuleBased` vs. `ML`).
5. **Observer Pattern:** `BudgetMonitor` evaluates transactions and actively publishes budget threshold alerts to dependent services (EmailNotifier, FirebaseNotifier).
6. **Builder Pattern:** `ReportBuilder` handles incremental step-wise assembly of the complex Monthly Report.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js (v20+ recommended for frontend standalone testing)
- Python 3.11+ (for standalone backend testing)

### Running the Application

For a convenient out-of-the-box local development server, run the entire stack through Docker Compose:

```bash
docker compose up --build
```
This deploys PostgreSQL, Redis, RabbitMQ, multiple custom service containers, and routes all traffic through the **Nginx API Gateway** on `localhost:8000`. 
Run the frontend server concurrently for development:

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

Verification scripts are executed securely through the local conda environment targeting standard `pytest` mechanisms within the microservices `/services/tests` boundary:

```bash
chmod +x run_tests.sh
./run_tests.sh
```