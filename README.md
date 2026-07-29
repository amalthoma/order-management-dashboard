# Order Management Dashboard - Backend

This is the backend foundation for the Order Management Dashboard, built with FastAPI and PostgreSQL.

## 1. Project Overview

The Order Management Dashboard backend is a robust, production-ready REST API built using **FastAPI** and **PostgreSQL**. It leverages **SQLAlchemy Async** for high-performance non-blocking database interactions and rigorously follows **Clean Architecture** principles. The system includes full order lifecycle management, advanced filtering and sorting, real-time WebSocket notifications, and external currency exchange integrations.

## 2. Features

- **JWT Authentication**
- **User Registration & Login**
- **Protected APIs**
- **Order CRUD**
- **Order Status Update**
- **Pagination**
- **Filtering**
- **Sorting**
- **Dashboard Summary**
- **Recent Orders**
- **Status Distribution**
- **Monthly Statistics**
- **WebSocket Real-time Notifications**
- **External Currency Exchange API**
- **Swagger Documentation**
- **Generic API Response Wrapper**
- **Repository Pattern**
- **Service Layer**
- **Async SQLAlchemy**
- **Alembic Migrations**
- **Docker Support**
- **Logging**
- **Exception Handling**

## 3. Technology Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance asynchronous web framework |
| **PostgreSQL** | Primary relational database |
| **SQLAlchemy Async** | Async Object Relational Mapper (ORM) |
| **Alembic** | Database migration tool |
| **Pydantic v2** | Data validation and serialization |
| **JWT** | Secure JSON Web Token authentication |
| **Passlib** | Secure password hashing |
| **Bcrypt** | Hashing algorithm |
| **HTTPX** | Asynchronous HTTP client |
| **WebSockets** | Real-time bi-directional communication |
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |

## 4. Project Structure

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── integrations/
│   ├── middleware/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── websocket/
│   └── main.py
├── alembic/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 5. Prerequisites

Before running the project, ensure you have the following installed:
- **Python 3.12+**
- **Docker Desktop**
- **PostgreSQL** (if running locally without Docker)

## 6. Installation

Follow these steps to run the project locally.

### Create and Activate Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Install Requirements

```bash
pip install -r requirements.txt
```

### Setup Environment Variables

Copy the example environment file:
```bash
# From the root directory
cp .env.example backend/.env
```

### Run Docker (PostgreSQL and Backend)

To run the entire stack (Database + Backend) using Docker Compose:
```bash
# From the root directory
docker compose up --build -d
```

### Run Alembic Migrations

```bash
cd backend
alembic upgrade head
```

### Run FastAPI Locally (without Docker)

If you prefer running FastAPI directly on your host (ensure PostgreSQL is running):
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 7. Environment Variables

Below is a sample configuration for your `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/order_management
SECRET_KEY=generate-a-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440
CURRENCY_API_URL=https://open.er-api.com/v6/latest
```
*(Do not expose real secrets in your source code repository.)*

## 8. API Documentation

Once the server is running, you can explore the interactive API documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 9. Authentication

The system uses highly secure JWT token-based authentication.

- **Register:** Create a new user account via the `/api/v1/auth/register` endpoint.
- **Login:** Authenticate via `/api/v1/auth/login` to receive your JWT access token.
- **JWT access token:** Must be sent in the `Authorization` header of subsequent requests.
- **Bearer Authentication:** Use the format `Bearer <token>` to access protected endpoints.

## 10. WebSocket

Real-time notifications are enabled via WebSockets to keep clients perfectly synchronized.

- **Endpoint:** `ws://localhost:8000/api/v1/ws/orders`
- **Supported events:**
  - `ORDER_STATUS_UPDATED`: Fired when an order's status changes.
  - `ping`: Keep-alive message sent by client.
  - `pong`: Automated server response to maintain connection.

When updating an order via the REST API, the new status and order details are immediately broadcast to all connected WebSocket clients to prevent stale data.

## 11. External API Integration

The platform handles real-time currency conversion using an external service:

- `GET /api/v1/currency/rate`
- `GET /api/v1/currency/convert`

Exchange rates are fetched from the external Exchange Rate API concurrently using the async `HTTPX` library.

## 12. Database Migration

Manage the database schema automatically using Alembic.

To generate a new migration after modifying models:
```bash
alembic revision --autogenerate -m "message"
```

To apply the latest migrations to your database:
```bash
alembic upgrade head
```

## 13. Docker

The project contains a fully configured Docker environment for seamless deployment.

Start all services:
```bash
docker compose up --build
```

Stop and tear down all services:
```bash
docker compose down
```

## 14. Architecture

- **Repository Pattern:** Abstracts all database queries into dedicated repository classes, keeping data access completely separate from business logic.
- **Service Layer:** Houses all business rules, orchestration, and schema transformations, ensuring endpoints remain strictly for routing.
- **Dependency Injection:** Leverages FastAPI's `Depends` for providing database sessions, configurations, and authenticated users securely.
- **Async SQLAlchemy:** Maximizes throughput and scalability by preventing thread-blocking during heavy database operations.
- **Clean Architecture:** Ensures clear separation of concerns, high testability, and enterprise-grade maintainability.

## 15. Future Improvements

- **Caching**
- **Unit Tests**
- **CI/CD Pipeline**
- **Monitoring**

