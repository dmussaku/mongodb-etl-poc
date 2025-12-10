from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def sample_etl_task():
    # Sample ETL task logic
    print("Executing sample ETL task")
    return "ETL task completed"



