import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def get_database_url():
    return os.getenv("DATABASE_URL")

def create_db_engine():
    return create_engine(get_database_url())

def get_session_local():
    engine = create_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Get a database session"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

def create_tables():
    """Create all tables"""
    engine = create_db_engine()
    Base.metadata.create_all(bind=engine)
