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
2. Create a virtual environment:   ```
   python -m venv env  ```
3. Install dependencies:   ```
   pip install -r requirements.txt   ```

## Running the Application

```
uvicorn app.main:app --reload
celery -A app.celery_worker worker
```

## Testing UI
```
http://127.0.0.1:8000/docs#/
```
