# FinSight

> **CS6.401 Software Engineering — Project 3 | Team 6**

FinSight is a personal finance management platform offering multi-source transaction ingestion, real-time budget tracking with email & push notifications, investment portfolio management, and an analytics dashboard with AI-powered savings recommendations.

**📄 Project Report:** [`Team6_Project_Report.pdf`](./Team6_Project_Report.pdf)

---

## Architecture

This system uses an **Event-Driven Microservices** architecture with asynchronous AMQP messaging (RabbitMQ) and synchronous REST HTTP communication.

### Subsystems
| Service | Stack | Purpose |
|---------|-------|---------|
| **Frontend SPA** | React 18 (Vite), TypeScript, Tailwind CSS | Interactive dashboard with charts, budgets, and portfolio |
| **API Gateway** | Nginx | Unified reverse-proxy routing |
| **Auth Service** | FastAPI, JWT, bcrypt | Registration, login, token management |
| **Transaction Service** | FastAPI, Plaid SDK | Multi-source ingestion via Adapter pattern |
| **Budget Service** | FastAPI, Pika | Budget evaluation and event publishing |
| **Analytics Service** | FastAPI, WeasyPrint | AI insights, investments, PDF reports |
| **Budget Worker** | Celery | Async notification dispatcher (Mailjet + Firebase) |
| **Database** | PostgreSQL 15, SQLAlchemy | Persistent relational storage |
| **Message Broker** | RabbitMQ | Fanout exchange for budget events |
| **Cache** | Redis | Currency rate caching |

### Design Patterns Implemented
1. **Factory Pattern** — `TransactionFactory` selects the correct parser based on data source
2. **Adapter Pattern** — `PlaidAdapter`, `CSVAdapter`, `ManualEntryAdapter` normalize heterogeneous data
3. **Observer Pattern** — `BudgetMonitor` notifies `EmailNotifier`, `InAppNotifier`, `LoggingObserver`
4. **Chain of Responsibility** — Currency conversion fallback (Cache → Live API → Hardcoded)
5. **Strategy Pattern** — `CategorizationService` supports rule-based vs. ML classification
6. **Builder Pattern** — `ReportBuilder` assembles complex monthly PDF reports step-by-step
7. **Pub/Sub** — RabbitMQ fanout exchange for asynchronous event broadcasting

---

## Team Contributions
| Member | Responsibility |
|--------|---------------|
| **Ananth** | Frontend Development & UI Engineering |
| **Lokesh** | Analytics Pipeline & Data Visualization |
| **Eshwar** | Core Business Logic & Microservice Architecture |
| **Rahul** | Core Logic, API Integrations & Systems Integration |
| **Ayush** | Core Logic, API Integrations & Systems Integration |

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js v18+ (for frontend development)
- Python 3.11+ (for standalone backend testing)

### Environment Setup
Create a `.env` file in the project root with the following keys:
```env
DATABASE_URL=postgresql://user:password@db:5432/finsight
SECRET_KEY=your-jwt-secret

# Plaid (Sandbox)
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret

# Mailjet
MAILJET_API_KEY=your_mailjet_api_key
MAILJET_SECRET_KEY=your_mailjet_secret_key
MAILJET_SENDER_EMAIL=sender@example.com
MAILJET_RECIPIENT_EMAIL=recipient@example.com

# Firebase
FIREBASE_CERT_PATH=/app/firebase-credentials.json
```

### Running the Application

Launch all services with Docker Compose:
```bash
docker compose up --build
```

Run the frontend dev server:
```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### Running Tests
```bash
chmod +x run_tests.sh
./run_tests.sh
```