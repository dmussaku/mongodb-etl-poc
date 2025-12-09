"""
ETL Job models for tracking ETL processes.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .database import Base
import uuid


class JobStatus(PyEnum):
    """ETL Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LoadType(PyEnum):
    """ETL Load type enumeration."""
    FULL = "full"
    INCREMENTAL = "incremental"


class ConnectionType(PyEnum):
    """Database connection type enumeration."""
    MONGODB = "mongodb"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    BIGQUERY = "bigquery"
    S3 = "s3"


class Connection(Base):
    """Database connection configuration."""
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    connection_type = Column(SQLEnum(ConnectionType), nullable=False)
    connection_string = Column(Text, nullable=False)  # Encrypted in production
    config = Column(JSON)  # Additional configuration parameters
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    source_jobs = relationship("ETLJob", foreign_keys="ETLJob.source_connection_id", back_populates="source_connection")
    dest_jobs = relationship("ETLJob", foreign_keys="ETLJob.dest_connection_id", back_populates="dest_connection")


class ETLJob(Base):
    """ETL Job configuration and metadata."""
    __tablename__ = "etl_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Source configuration
    source_connection_id = Column(Integer, ForeignKey("connections.id"), nullable=False)
    source_table = Column(String(255), nullable=False)  # Collection/table name
    aggregation_pipeline = Column(JSON)  # MongoDB aggregation pipeline or SQL query
    
    # Destination configuration
    dest_connection_id = Column(Integer, ForeignKey("connections.id"), nullable=False)
    dest_table = Column(String(255), nullable=False)
    
    # ETL configuration
    load_type = Column(SQLEnum(LoadType), default=LoadType.FULL)
    incremental_column = Column(String(255))  # Column for incremental loading
    masking_config = Column(JSON)  # Field masking configuration
    transformation_config = Column(JSON)  # Custom transformation rules
    
    # Scheduling
    schedule_cron = Column(String(100))  # Cron expression for scheduling
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))  # User who created the job
    
    # Relationships
    source_connection = relationship("Connection", foreign_keys=[source_connection_id])
    dest_connection = relationship("Connection", foreign_keys=[dest_connection_id])
    runs = relationship("JobRun", back_populates="job")


class JobRun(Base):
    """Individual ETL job execution record."""
    __tablename__ = "job_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("etl_jobs.id"), nullable=False)
    
    # Execution details
    celery_task_id = Column(String(255), index=True)  # Celery task ID for tracking
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Results
    records_processed = Column(Integer, default=0)
    records_success = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Error details
    error_message = Column(Text)
    logs = Column(Text)
    
    # Metadata
    triggered_by = Column(String(50))  # 'manual', 'schedule', 'api'
    config_snapshot = Column(JSON)  # Job configuration at time of execution
    
    # Relationships
    job = relationship("ETLJob", back_populates="runs")