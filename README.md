# Order Management Dashboard - Backend

This is the backend foundation for the Order Management Dashboard, built with FastAPI and PostgreSQL.

## Getting Started

Follow these steps to run the project locally.

### 1. Create and Activate Virtual Environment
`ash
cd backend
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
`

### 2. Install Packages
`ash
pip install -r requirements.txt
`

### 3. Setup Environment Variables
Copy the example environment file:
`ash
# From the root directory
cp .env.example backend/.env
`

### 4. Run Docker (PostgreSQL and Backend)
To run the entire stack (Database + Backend) using Docker Compose:
`ash
# From the root directory
docker-compose up --build -d
`

### 5. Run Alembic Migrations
*(Note: Alembic is installed but migrations directory needs to be initialized lembic init alembic if not present yet)*
`ash
cd backend
alembic upgrade head
`

### 6. Run FastAPI Locally (without Docker)
If you prefer running FastAPI directly on your host (ensure PostgreSQL is running):
`ash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
`
