import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import config

engine = create_engine(config.db.connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    logging.info("Initialized the db")
