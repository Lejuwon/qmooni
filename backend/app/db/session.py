from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

Base = declarative_base()

# DATABASE_URL = os.getenv("DATABASE_URL")
# engine = create_engine(DATABASE_URL)
engine = create_engine(
    settings.database_url,            # ← settings.database_url 사용
    pool_pre_ping=True
)
logging.info(f"🔗 Connected to database: {engine.url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()