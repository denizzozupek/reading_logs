from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

Base = declarative_base() #a factory function that creates a base class for your ORM models, connecting Python classes to database tables

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
