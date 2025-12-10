from celery import shared_task
import logging
from .services import PipelineExecutionService

logger = logging.getLogger(__name__)


@shared_task
def run_pipeline_task(pipeline_id):
    """
    Execute an ETL pipeline by Pipeline ID.
    
    Args:
        pipeline_id: The ID of the Pipeline model to execute
        
    Returns:
        dict: Execution result with status and metadata
    """
    logger.info(f"Starting run_pipeline_task with pipeline_id: {pipeline_id}")
    
    service = PipelineExecutionService(pipeline_id)
    return service.execute()


@shared_task
def sample_etl_task():
    """Sample ETL task for testing purposes"""
    logger.info("Starting sample_etl_task")
    # Sample ETL task logic
    print("Executing sample ETL task")
    logger.info("Completed sample_etl_task")
    return "ETL task completed"

