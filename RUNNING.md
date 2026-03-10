# How to Run UofTHacks 13 Project

## Prerequisites
- Docker and Docker Compose installed (Recommended).
- Node.js and Python 3.11+ installed (for local non-Docker development).

## Running with Docker Compose (Recommended)
1. Open a terminal in the project root directory.
2. Start the services using Docker Compose:
   ```bash
   docker compose up --build
   ```
   This will start the backend API, workers, frontend, Redis, MongoDB, and Redpanda.

3. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API Docs**: http://localhost:8000/docs

---

## Running Locally (Without Docker)

If you prefer to run the application components directly on your machine instead of using Docker, follow these steps. Note that you must still have Redis, MongoDB, and Kafka/RedPanda running locally. 

### 1. Backend API
1. Open a terminal and navigate to the `backend` directory.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   *The backend will be available at http://localhost:8000*

### 2. Frontend
1. Open a new terminal and navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The frontend will be available at http://localhost:5173 (or as indicated by Vite).*
