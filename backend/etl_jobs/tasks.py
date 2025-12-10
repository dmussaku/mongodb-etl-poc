from celery import shared_task

@shared_task
def sample_etl_task():
    # Sample ETL task logic
    print("Executing sample ETL task")
    return "ETL task completed"
