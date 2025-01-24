# FastAPI Template

A modern FastAPI template with SQLAlchemy integration.

## Features

- FastAPI framework
- SQLModel
- Celery Worker
- Connection to Redis broker
- Structured project layout

## Installation

1. Clone the repository
2. Create a virtual environment:   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate   ```
3. Install dependencies:   ```bash
   pip install -r requirements.txt   ```

## Running the Application

```bash
uvicorn app.main 
