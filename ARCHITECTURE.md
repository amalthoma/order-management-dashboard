# System Architecture

This document provides a high-level overview of the architectural decisions and patterns used in the Order Management Dashboard.

## High-Level Architecture
The system follows a classic decoupled client-server architecture:
- **Frontend**: A Single Page Application (SPA) built with React and Vite. It serves as the presentation layer, consuming REST APIs and WebSockets.
- **Backend**: A robust REST API built with FastAPI and PostgreSQL. It handles all business logic, data persistence, authentication, and external integrations.
- **Database**: PostgreSQL handles persistent relational storage.
- **Containerization**: Docker Compose orchestrates the entire stack (Database, Backend, Frontend) for seamless local development and deployment.

## Backend Architecture

The backend strictly adheres to **Clean Architecture** principles to separate concerns and ensure testability.

### 1. Repository Pattern
Data access is entirely abstracted. The Service Layer does not contain any direct SQLAlchemy ORM queries. Instead, it injects dependencies from the Repository Layer (e.g., OrderRepository). This makes it trivial to mock database calls during testing or swap underlying database technologies in the future without breaking business logic.

### 2. Service Layer
The Service Layer is the brain of the application. It receives validated Pydantic models from the API routers, applies business rules, interacts with external services, orchestrates repositories, and returns structured data. The API routers are kept completely "dumb," acting solely as HTTP transport handlers.

### 3. Authentication Flow
We utilize stateless **JWT (JSON Web Token)** authentication.
- Users authenticate via /api/v1/auth/login.
- The server validates credentials and returns an access token signed with a secure secret key.
- The client stores this token and passes it in the Authorization: Bearer <token> header for all subsequent requests.
- FastAPI's dependency injection (Depends(get_current_user)) intercepts and verifies the token on protected routes.

### 4. WebSocket Flow
To keep clients perfectly synchronized without aggressive polling:
- The backend maintains an active ConnectionManager.
- When the Service Layer processes an order status update via PATCH, it instantly triggers an event to the ConnectionManager.
- The manager broadcasts an ORDER_STATUS_UPDATED JSON payload to all connected WebSocket clients.
- The React frontend receives this payload and automatically invalidates the React Query cache, triggering a silent background refetch that updates the UI in real-time.

### 5. External API Integration (Currency)
The backend acts as a secure proxy to external services to avoid exposing logic or keys on the client.
- It utilizes the asynchronous HTTPX client for non-blocking network calls.
- The CurrencyService orchestrates fetching real-time conversion rates and formats the response for the frontend widget.

## Frontend Architecture

The frontend is structured to maximize scalability and developer velocity.

### 1. React Query Flow
We use **TanStack React Query** for all server-state management.
- **Fetching**: Custom hooks (e.g., useOrders, useDashboard) wrap Axios API calls and map directly to React Query keys. This provides automatic caching, deduping, and background refetching.
- **Mutations**: useCreateOrder and useUpdateOrderStatus utilize React Query mutations. Upon success, they seamlessly invalidate specific query keys to update the UI without manual state management.
- **Optimistic Updates**: For status changes, the frontend performs an optimistic update on the local cache before the server responds, ensuring instantaneous UI feedback.

### 2. Folder Structure
- pi/: Defines static endpoint dictionaries.
- components/: Modular UI elements grouped by type (charts, common, orms, layout, 	ables).
- contexts/: React Contexts strictly reserved for global authentication state.
- hooks/: Reusable React Query wrappers and custom logic (like useWebSocket).
- lib/: Third-party infrastructure configuration (e.g., the global Axios instance with interceptors).
- pages/: Route-level components that orchestrate state and layout.
- providers/: Centralized context providers that wrap the App root.
- schemas/: Zod validation schemas that perfectly mirror backend Pydantic models.
- services/: Axios network request abstractions.
- 	ypes/: Strict TypeScript interfaces mirroring backend responses.
