"""
Health check endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
import pika
import pymongo
from datetime import datetime

from ..config import settings
from ..models import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": settings.app_name
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with all dependencies."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": settings.app_name,
        "checks": {}
    }
    
    # Check PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["postgres"] = "healthy"
    except Exception as e:
        health_status["checks"]["postgres"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.celery_broker_url))
        connection.close()
        health_status["checks"]["rabbitmq"] = "healthy"
    except Exception as e:
        health_status["checks"]["rabbitmq"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check MongoDB
    try:
        client = pymongo.MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        health_status["checks"]["mongodb"] = "healthy"
    except Exception as e:
        health_status["checks"]["mongodb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status