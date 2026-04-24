# Architecture Migration Report: Monolith to Event-Driven

## 1. The Initial System
The FinSight application originally operated as a tightly integrated monolithic FastAPI backend. While design patterns such as Factory, Strategy, and Chain of Responsibility were well-implemented, the system utilized a synchronous Observer Pattern within the [BudgetMonitor](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/budget/monitor.py#10-108). When a transaction was ingested, the request thread would block to evaluate categorical budgets and sequentially trigger each notification mechanism (Email, Push, Logging), leading to potential latency and single points of failure. The `Ingestion` logic (parsing files and external bank connections) resided within the exact same process as the `Core Logic`, leaving the system inflexible under heavy ingestion loads.

## 2. Changes Made
We adopted a Pragmatic Event-Driven Architecture (EDA), meaning we strategically decoupled processing layers while maintaining the centralized PostgreSQL database for simplicity. 
1. **Message Broker Introduced**: Integrated RabbitMQ (`pika`) to securely handle asynchronous communication via Publisher-Subscriber models.
2. **Synchronous Unblocking**: Decoupled the [BudgetMonitor](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/budget/monitor.py#10-108) so its evaluations now asynchronously publish `BudgetThresholdExceeded` events, consumed by a background daemon.
3. **Monolith Decoupling (Service Split)**: 
   - Created **Service A (Ingestion)** running natively on port 8001. Plaid syncs, manual injections, and CSV mappings live exclusively here. Upon successful ingestion, the service publishes a `TransactionIngested` event globally.
   - Restructured **Service B (Core Logic)** to purely operate on port 8000 handling user interaction, whilst a persistent background consumer dynamically triggers Categorization Strategies and the [BudgetMonitor](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/budget/monitor.py#10-108) upon catching `TransactionIngested` events.

## 3. Why We Made These Changes
- **Isolation of Workloads**: Bulk ingestion processes or API delays (like connecting to Plaid) will no longer drain resources from the core frontend REST servicing layer.
- **Resilience**: If the notification service (e.g. Email Provider) timeouts, it no longer breaks the transaction commit cycle or affects the user’s response timing.
- **Scalability**: By preparing a pub-sub foundation, the ecosystem is now natively ready for independent vertical scaling (e.g., spinning up multiple `Ingestion` containers).

## 4. How the Changes Were Implemented
- **Infrastructure**: Added RabbitMQ (`rabbitmq:3-management`) to the Docker cluster. Upgraded [docker-compose.yml](file:///home/ayush/Sem8/SE/Project/P3/mine/docker-compose.yml) to spin up `mine-ingestion` alongside `mine-backend`.
- **Code Refactoring**: Strip-mined the `ingestion_router` from [main.py](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/main.py) and planted it into [main_ingestion.py](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/main_ingestion.py). Augmented transaction db commits with asynchronous Pika event publishers. Created robust [start_core_subscriber](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/core/subscriber.py#54-77) daemon threads operating in FastAPI's contextual lifespan.
- **Testing**: Reconfigured Python unit tests (specifically [tests.py](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/tests.py)) to leverage Mock objects wrapping `pika.BlockingConnection` enabling logic tests to persist perfectly without active docker containers.

## 5. What Things Dynamically Changed
- The frontend / external integrations now route ingestion events to port `8001` directly avoiding `8000`.
- The latency of transaction addition dropped immensely due to deferring analytics and categorization to the RabbitMQ queues.
- [BudgetMonitor](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/budget/monitor.py#10-108) observers were functionally replaced by queue listeners.

## 6. How We Ensured Continued Reliability (Verification)
Stringent testing was carried out post-implementation:
1. **Unit Testing**: Ran `python3 tests.py` verifying all mocked event loops, strategy evaluations, and legacy chain-of-commands. All tests cleared continuously demonstrating the logical integrity wasn't compromised.
2. **Infrastructure Validation**: Utilized `docker compose up --build -d` alongside user-level group contexts to ensure the new `mine-ingestion-1` and dependencies ([db](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/temp.db), `rabbitmq`) launched in a unified network.
3. **End-to-End Tracing script**: Crafted [test_e2e.py](file:///home/ayush/Sem8/SE/Project/P3/mine/backend/test_e2e.py) to authentically log into the API, fetch a JWT Token, hit the isolated `/ingestion/manual` port 8001, and verify via Docker logs that the `backend` daemon correctly pulled the event from RabbitMQ, categorized the transactions, and issued Budget limit alerts!
