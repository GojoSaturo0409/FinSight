# FinSight Architecture Flowcharts

The following diagrams illustrate how the data execution flows in the system both before and after the transition to the Event-Driven Architecture.

## 1. Before: Tightly Coupled Monolith (Synchronous)

In the initial state, all routes and logic handlers (Ingestion, Categorization, Budgeting) were processed procedurally on a single server block (`mine-backend:8000`). When a transaction was added, the API blocked the user's requesting thread until all observer pattern notifications (Email, Push, Logging) consecutively finished.

```mermaid
flowchart TD
    User((User or Web Frontend))
    DB[(PostgreSQL)]
    
    subgraph Monolith[mine-backend-1 Port 8000]
        Router[Ingestion Router]
        Factory[Transaction Factory]
        Strategy[Categorization Strategy]
        Monitor[Budget Monitor]
        
        subgraph Observers[Observers]
            Email[Email Notifier]
            Push[Push Notifier]
            Log[Logging Observer]
        end
    end

    User -->|POST ingestion/manual| Router
    Router -->|Parses Data| Factory
    Factory -->|Assigns Category| Strategy
    Strategy -->|Saves Tx| DB
    Strategy -->|Calls evaluate| Monitor
    Monitor -->|Synchronous Trigger| Email
    Monitor -->|Synchronous Trigger| Push
    Monitor -->|Synchronous Trigger| Log
    Log -->|Returns OK| User

    style Monitor fill:#ffcccc,stroke:#ff0000,stroke-width:2px,stroke-dasharray: 5 5
    style Email fill:#ffcccc
    style Push fill:#ffcccc
    style Log fill:#ffcccc
```

## 2. After: Pragmatic Event-Driven Architecture (Asynchronous)

In the revised state, we isolated the **Ingestion Service** (`mine-ingestion:8001`) from the **Core Logic** (`mine-backend:8000`). We introduced a **RabbitMQ** Message Broker to decouple processes via Pub/Sub. When user transactions hit the ingestion gateway, it commits to the DB and fires an asynchronous event (`TransactionIngested`) without blocking the user. Core background tasks pull these events and independently alert the end-user via `BudgetThresholdExceeded` events recursively.

```mermaid
flowchart TD
    User((User or Web Frontend))
    DB[(Shared PostgreSQL)]
    RabbitMQ(((RabbitMQ Broker)))

    subgraph ServiceA[mine-ingestion-1 Port 8001]
        RouterA[Ingestion Router]
        FactoryA[Transaction Factory]
        PublisherA[Event Publisher]
    end

    subgraph ServiceB[mine-backend-1 Port 8000]
        ConsumerCore((Background Subscriber))
        StrategyB[Categorization Strategy]
        MonitorB[Budget Monitor]
        PublisherB[Budget Publisher]

        ConsumerBudget((Budget Subscriber))
        subgraph ObserversB[Observers]
            EmailB[Email Notifier]
            PushB[Push Notifier]
            LogB[Logging Observer]
        end
    end

    User -->|POST ingestion/manual| RouterA
    RouterA -->|Parses Data| FactoryA
    FactoryA -->|Saves Tx| DB
    FactoryA -->|Calls| PublisherA
    PublisherA -->|Publishes TransactionIngested| RabbitMQ
    PublisherA -->|Returns 200 OK immediately| User

    RabbitMQ -->|Consumes TransactionIngested| ConsumerCore
    ConsumerCore -->|Executes Strategy| StrategyB
    StrategyB -->|Updates Category| DB
    StrategyB -->|Calls evaluate| MonitorB
    MonitorB -->|Calls| PublisherB
    PublisherB -->|Publishes BudgetThresholdExceeded| RabbitMQ

    RabbitMQ -->|Consumes BudgetThresholdExceeded| ConsumerBudget
    ConsumerBudget -->|Async Trigger| EmailB
    ConsumerBudget -->|Async Trigger| PushB
    ConsumerBudget -->|Async Trigger| LogB

    style RabbitMQ fill:#ffe6cc,stroke:#ff9900,stroke-width:3px
    style ConsumerCore fill:#e6ffcc,stroke:#33cc33
    style ConsumerBudget fill:#e6ffcc,stroke:#33cc33
    style PublisherA fill:#cce6ff,stroke:#0066ff
    style PublisherB fill:#cce6ff,stroke:#0066ff
```
