from celery import shared_task
import logging
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Pipeline, JobExecution
from .pipeline import run_pipeline

logger = logging.getLogger(__name__)


@shared_task
def run_pipeline_task(pipeline_id):
    """
    Execute an ETL pipeline by Pipeline ID and log the execution.
    
    Args:
        pipeline_id: The ID of the Pipeline model to execute
        
    Returns:
        dict: Execution result with status and metadata
    """
    logger.info(f"Starting run_pipeline_task with pipeline_id: {pipeline_id}")
    execution = None
    
    try:
        # Get the pipeline configuration
        pipeline = Pipeline.objects.get(id=pipeline_id, is_active=True, is_enabled=True)
        logger.info(f"Starting pipeline execution for: {pipeline.name}")
        
        # Create JobExecution record
        execution = JobExecution.objects.create(
            pipeline=pipeline,
            status="running",
            started_at=timezone.now(),
            execution_id=str(uuid.uuid4())
        )
        
        # Prepare source configuration
        source_config = {
            "type": "mongodb",  # Assuming MongoDB source based on your models
            "connection_url": pipeline.source_uri,
            "database": pipeline.source_database,
            "collection": pipeline.source_table,
            "aggregation_pipeline": pipeline.source_aggregation_query,
            # "write_disposition": pipeline.load_type
        }
        
        # Add incremental configuration if applicable
        if pipeline.load_type == "incremental" and pipeline.incremental_key:
            source_config["incremental_key"] = pipeline.incremental_key
            if pipeline.incremental_strategy:
                source_config["incremental_strategy"] = pipeline.incremental_strategy
        
        # Prepare destination configuration
        destination_config = {
            "type": "mongodb",  # Assuming MongoDB destination based on your models
            "connection_url": pipeline.destination_uri,
            "database": pipeline.destination_database,
            "collection": pipeline.destination_table
        }
        
        # Run the pipeline
        load_info = run_pipeline(
            source_config=source_config,
            destination_config=destination_config,
            pipeline_name=pipeline.name,
            dev_mode=False
        )
        
        # Calculate duration
        completed_at = timezone.now()
        duration = (completed_at - execution.started_at).total_seconds()
        
        # Extract metrics from load_info
        rows_processed = 0
        rows_inserted = 0
        rows_failed = 0
        files_processed = 0
        total_file_size = 0
        
        logger.info(f"Load info structure: {type(load_info)}")
        logger.info(f"Load info attributes: {dir(load_info)}")
        logger.info(f"Load info loads_ids: {getattr(load_info, 'loads_ids', 'N/A')}")
        
        # DLT LoadInfo structure analysis
        if hasattr(load_info, 'metrics') and load_info.metrics:
            logger.info(f"Found metrics in load_info: {load_info.metrics}")
            
            # Iterate through metrics by load_id
            for load_id, metrics_list in load_info.metrics.items():
                logger.info(f"Processing metrics for load_id: {load_id}")
                
                for metrics in metrics_list:
                    logger.info(f"Metrics object type: {type(metrics)}")
                    logger.info(f"Metrics attributes: {dir(metrics)}")
                    
                    # Extract job metrics (individual files/jobs)
                    if hasattr(metrics, 'job_metrics') and metrics.job_metrics:
                        logger.info(f"Found job_metrics: {metrics.job_metrics}")
                        
                        for job_id, job_metrics in metrics.job_metrics.items():
                            logger.info(f"Processing job {job_id}: {job_metrics}")
                            # job_metrics is LoadJobMetrics
                            files_processed += 1
                    
                    # Extract table metrics (aggregated by table)
                    if hasattr(metrics, 'table_metrics') and metrics.table_metrics:
                        logger.info(f"Found table_metrics: {metrics.table_metrics}")
                        
                        for table_name, table_metrics in metrics.table_metrics.items():
                            logger.info(f"Processing table {table_name}: {table_metrics}")
                            # table_metrics is DataWriterMetrics
                            if hasattr(table_metrics, 'items_count'):
                                rows_processed += table_metrics.items_count
                                rows_inserted += table_metrics.items_count  # For inserts, processed = inserted
                                logger.info(f"Added {table_metrics.items_count} rows from table {table_name}")
                            
                            if hasattr(table_metrics, 'file_size'):
                                total_file_size += table_metrics.file_size
        
        # Check load packages for failed jobs
        if hasattr(load_info, 'load_packages') and load_info.load_packages:
            logger.info(f"Found {len(load_info.load_packages)} load packages")
            
            for package in load_info.load_packages:
                logger.info(f"Package load_id: {package.load_id}")
                
                if hasattr(package, 'jobs') and package.jobs:
                    logger.info(f"Package jobs structure: {package.jobs}")
                    
                    # Count failed jobs
                    failed_jobs = package.jobs.get('failed_jobs', [])
                    rows_failed += len(failed_jobs)
                    
                    if failed_jobs:
                        logger.warning(f"Found {len(failed_jobs)} failed jobs in package {package.load_id}")
                        for failed_job in failed_jobs:
                            logger.error(f"Failed job: {failed_job}")
        
        # Create comprehensive logs
        logs = f"""Pipeline executed successfully.
Load IDs: {getattr(load_info, 'loads_ids', [])}
Destination: {getattr(load_info, 'destination_name', 'Unknown')}
Dataset: {getattr(load_info, 'dataset_name', 'Unknown')}
Files Processed: {files_processed}
Total File Size: {total_file_size} bytes
Rows Processed: {rows_processed}
Rows Inserted: {rows_inserted}
Failed Jobs: {rows_failed}
Load Info Details: {str(load_info)}"""
        
        logger.info(f"Final metrics - Rows processed: {rows_processed}, Rows inserted: {rows_inserted}, Failed jobs: {rows_failed}")
        
        # Update execution record with success
        execution.status = "success"
        execution.completed_at = completed_at
        execution.duration_seconds = Decimal(str(duration))
        execution.rows_processed = rows_processed
        execution.rows_inserted = rows_inserted
        execution.rows_failed = rows_failed
        execution.files_processed = files_processed
        execution.total_file_size = total_file_size
        execution.load_ids = getattr(load_info, 'loads_ids', [])
        execution.destination_name = getattr(load_info, 'destination_name', None)
        execution.dataset_name = getattr(load_info, 'dataset_name', None)
        execution.logs = logs
        execution.save()
        
        logger.info(f"Pipeline {pipeline.name} completed successfully in {duration:.2f} seconds")
        
        return {
            "status": "success",
            "execution_id": execution.execution_id,
            "duration_seconds": float(duration),
            "rows_processed": rows_processed,
            "rows_inserted": rows_inserted,
            "rows_failed": rows_failed,
            "files_processed": files_processed,
            "total_file_size": total_file_size
        }
        
    except Pipeline.DoesNotExist:
        error_msg = f"Pipeline with ID {pipeline_id} not found or not active/enabled"
        logger.error(error_msg)
        return {"status": "failed", "error": error_msg}
        
    except Exception as e:
        error_msg = f"Pipeline execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Update execution record with failure if it exists
        if execution:
            execution.status = "failed"
            execution.completed_at = timezone.now()
            execution.error_message = error_msg
            execution.logs = f"Pipeline execution failed with error: {str(e)}"
            
            if execution.started_at:
                duration = (execution.completed_at - execution.started_at).total_seconds()
                execution.duration_seconds = Decimal(str(duration))
            
            execution.save()
        
        return {
            "status": "failed", 
            "error": error_msg,
            "execution_id": execution.execution_id if execution else None
        }


@shared_task
def sample_etl_task():
    """Sample ETL task for testing purposes"""
    logger.info("Starting sample_etl_task")
    # Sample ETL task logic
    print("Executing sample ETL task")
    logger.info("Completed sample_etl_task")
    return "ETL task completed"

