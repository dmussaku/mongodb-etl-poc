"""
Celery tasks for ETL operations.
"""
import logging
from datetime import datetime
from typing import Any, Dict
from sqlalchemy.orm import Session

from .celery import celery
from ..models import engine, JobRun, ETLJob, JobStatus
from ..etl.pipeline import ETLPipeline

logger = logging.getLogger(__name__)


@celery.task(bind=True)
def test_celery_task(self, message: str) -> Dict[str, Any]:
    """
    Test task to verify Celery connectivity.
    """
    logger.info(f"Processing test task with message: {message}")
    
    # Simulate some work
    import time
    time.sleep(2)
    
    return {
        "task_id": self.request.id,
        "message": f"Processed: {message}",
        "timestamp": datetime.utcnow().isoformat(),
        "worker": self.request.hostname
    }


@celery.task(bind=True)
def run_etl_job(self, job_run_id: int) -> Dict[str, Any]:
    """
    Execute an ETL job.
    
    Args:
        job_run_id: ID of the JobRun record
        
    Returns:
        Dictionary with execution results
    """
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get job run and related job
        job_run = db.query(JobRun).filter(JobRun.id == job_run_id).first()
        if not job_run:
            raise ValueError(f"Job run {job_run_id} not found")
        
        job = db.query(ETLJob).filter(ETLJob.id == job_run.job_id).first()
        if not job:
            raise ValueError(f"ETL job {job_run.job_id} not found")
        
        # Update status to running
        job_run.status = JobStatus.RUNNING
        db.commit()
        
        logger.info(f"Starting ETL job run {job_run_id} for job {job.name}")
        
        # Create and execute ETL pipeline
        pipeline = ETLPipeline(job, job_run, db)
        result = pipeline.execute()
        
        # Update job run with results
        job_run.status = JobStatus.SUCCESS
        job_run.completed_at = datetime.utcnow()
        job_run.records_processed = result.get("records_processed", 0)
        job_run.records_success = result.get("records_success", 0) 
        job_run.records_failed = result.get("records_failed", 0)
        job_run.logs = result.get("logs", "")
        
        db.commit()
        
        logger.info(f"ETL job run {job_run_id} completed successfully")
        
        return {
            "job_run_id": job_run_id,
            "status": "success",
            "records_processed": result.get("records_processed", 0),
            "completed_at": job_run.completed_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"ETL job run {job_run_id} failed: {str(e)}")
        
        # Update job run with error
        if 'job_run' in locals():
            job_run.status = JobStatus.FAILED
            job_run.completed_at = datetime.utcnow()
            job_run.error_message = str(e)
            db.commit()
        
        # Re-raise the exception for Celery to handle
        raise self.retry(exc=e, countdown=60, max_retries=3)
        
    finally:
        db.close()


@celery.task(bind=True)
def scheduled_etl_job(self, job_id: int) -> Dict[str, Any]:
    """
    Task for scheduled ETL jobs.
    
    Args:
        job_id: ID of the ETL job to run
        
    Returns:
        Dictionary with execution results
    """
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
        if not job or not job.is_active:
            logger.warning(f"Scheduled job {job_id} not found or inactive")
            return {"status": "skipped", "reason": "job not found or inactive"}
        
        # Create new job run
        job_run = JobRun(
            job_id=job_id,
            status=JobStatus.PENDING,
            triggered_by="schedule",
            celery_task_id=self.request.id,
            config_snapshot={
                "source_table": job.source_table,
                "dest_table": job.dest_table,
                "load_type": job.load_type.value if job.load_type else None,
            }
        )
        db.add(job_run)
        db.commit()
        db.refresh(job_run)
        
        # Execute the ETL job
        return run_etl_job.delay(job_run.id).get()
        
    finally:
        db.close()