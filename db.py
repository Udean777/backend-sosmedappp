import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if "BASE_URL" not in os.environ:
    raise ValueError("The BASE_URL environment variable is not set.")

engine = create_engine(os.getenv("BASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()