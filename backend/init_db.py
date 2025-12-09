#!/usr/bin/env python3
"""
Simple script to initialize database tables.
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.models.etl import ETLJob, JobRun, Connection
from src.config import settings

# Create engine
engine = create_engine(settings.database_url)

# Create all tables
Base = declarative_base()

# Import all models to register them
ETLJob.metadata.create_all(bind=engine)
print("Database tables created successfully!")