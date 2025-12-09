"""
ETL job management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models import get_db, ETLJob, JobRun, Connection, JobStatus
from ..worker.tasks import test_celery_task, run_etl_job

router = APIRouter()


@router.get("/jobs")
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all ETL jobs."""
    jobs = db.query(ETLJob).offset(skip).limit(limit).all()
    return {
        "jobs": jobs,
        "count": len(jobs),
        "skip": skip,
        "limit": limit
    }


@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get specific ETL job details."""
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/runs")
async def list_job_runs(
    job_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List runs for a specific job."""
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    runs = db.query(JobRun).filter(JobRun.job_id == job_id).offset(skip).limit(limit).all()
    return {
        "runs": runs,
        "count": len(runs),
        "skip": skip,
        "limit": limit,
        "job_id": job_id
    }


@router.post("/jobs/{job_id}/run")
async def trigger_job_run(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger an ETL job run."""
    job = db.query(ETLJob).filter(ETLJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Create new job run record
    job_run = JobRun(
        job_id=job_id,
        status=JobStatus.PENDING,
        triggered_by="manual",
        config_snapshot={
            "source_table": job.source_table,
            "dest_table": job.dest_table,
            "load_type": job.load_type.value if job.load_type else None,
            "aggregation_pipeline": job.aggregation_pipeline,
            "masking_config": job.masking_config
        }
    )
    db.add(job_run)
    db.commit()
    db.refresh(job_run)
    
    # Queue the ETL task
    task = run_etl_job.delay(job_run.id)
    job_run.celery_task_id = task.id
    db.commit()
    
    return {
        "message": "Job run queued successfully",
        "job_run_id": job_run.id,
        "celery_task_id": task.id,
        "status": job_run.status.value
    }


@router.get("/connections")
async def list_connections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all database connections."""
    connections = db.query(Connection).offset(skip).limit(limit).all()
    return {
        "connections": connections,
        "count": len(connections),
        "skip": skip,
        "limit": limit
    }


@router.post("/test-celery")
async def test_celery():
    """Test Celery task queue connectivity."""
    task = test_celery_task.delay("Hello from FastAPI!")
    return {
        "message": "Test task queued",
        "task_id": task.id,
        "status": task.status
    }