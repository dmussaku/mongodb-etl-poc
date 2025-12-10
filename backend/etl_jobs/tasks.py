from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def sample_etl_task():
    # Sample ETL task logic
    print("Executing sample ETL task")
    return "ETL task completed"


@shared_task
def periodic_health_check():
    """
    Periodic task that runs regularly to perform system health checks.
    Can be scheduled to run every X seconds/minutes/hours.
    """
    logger.info(f"Health check executed at {timezone.now()}")
    return "Health check completed"


@shared_task
def periodic_mongodb_sync():
    """
    Periodic task for syncing data from MongoDB.
    Example of a task that can be scheduled daily or at specific times.
    """
    logger.info(f"MongoDB sync started at {timezone.now()}")
    # Add your MongoDB sync logic here
    logger.info("MongoDB sync completed")
    return "MongoDB sync completed"


@shared_task
def periodic_cleanup():
    """
    Periodic task for database cleanup and maintenance.
    Useful for removing old records, archiving data, etc.
    """
    logger.info(f"Cleanup task started at {timezone.now()}")
    # Add your cleanup logic here
    logger.info("Cleanup completed")
    return "Cleanup completed"
