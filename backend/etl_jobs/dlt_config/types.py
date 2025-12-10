"""
Data source and destination type definitions for the ETL pipeline.
"""
from enum import Enum


class SourceType(Enum):
    """Supported data source types"""
    MONGODB = "mongodb"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    API = "api"
    FILE = "file"


class DestinationType(Enum):
    """Supported data destination types"""
    MONGODB = "mongodb"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    S3 = "s3"
    BIGQUERY = "bigquery"