from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from .config import settings

DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password.get_secret_value()}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# Create the SQLAlchemy engine for PostgreSQL
engine = create_engine(DATABASE_URL)

# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_engine():
    return engine

# Function to create the database tables (runs on startup)
def create_db():
    Base.metadata.create_all(bind=engine)


