from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Plot Scraper"
    PROJECT_DESCRIPTION: str = "Async plot scraping service"
    API_STR: str = "/api"
    
    # Database settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "jommy348"
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "plotDB"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:32768"
    CELERY_RESULT_BACKEND: str = "redis://localhost:32768"

    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    class Config:
        case_sensitive = True

settings = Settings() 