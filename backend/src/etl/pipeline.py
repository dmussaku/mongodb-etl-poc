"""
ETL Pipeline implementation using dlt.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import dlt
import pymongo
from datetime import datetime

from ..models import ETLJob, JobRun, Connection, ConnectionType, LoadType
from ..config import settings

logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    ETL Pipeline executor using dlt framework.
    """
    
    def __init__(self, job: ETLJob, job_run: JobRun, db: Session):
        self.job = job
        self.job_run = job_run
        self.db = db
        
    def execute(self) -> Dict[str, Any]:
        """
        Execute the ETL pipeline.
        
        Returns:
            Dict containing execution results and metrics
        """
        logger.info(f"Executing ETL job: {self.job.name}")
        
        try:
            # Get source and destination connections
            source_conn = self.db.query(Connection).filter(Connection.id == self.job.source_connection_id).first()
            dest_conn = self.db.query(Connection).filter(Connection.id == self.job.dest_connection_id).first()
            
            if not source_conn or not dest_conn:
                raise ValueError("Source or destination connection not found")
            
            # Create dlt pipeline
            pipeline = dlt.pipeline(
                pipeline_name=f"etl_job_{self.job.id}",
                destination=self._get_dlt_destination(dest_conn),
                dataset_name=self._get_dataset_name()
            )
            
            # Extract data from source
            source_data = self._extract_data(source_conn)
            
            # Apply transformations and masking
            transformed_data = self._transform_data(source_data)
            
            # Load data to destination
            load_info = pipeline.run(transformed_data, table_name=self.job.dest_table)
            
            # Calculate metrics
            records_processed = load_info.load_packages[0].jobs[0].job_file_info.rows_count if load_info.load_packages else 0
            
            logger.info(f"ETL job completed. Processed {records_processed} records")
            
            return {
                "records_processed": records_processed,
                "records_success": records_processed,
                "records_failed": 0,
                "logs": f"Successfully processed {records_processed} records",
                "load_info": str(load_info)
            }
            
        except Exception as e:
            logger.error(f"ETL job failed: {str(e)}")
            return {
                "records_processed": 0,
                "records_success": 0,
                "records_failed": 0,
                "logs": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def _extract_data(self, source_conn: Connection) -> List[Dict[str, Any]]:
        """
        Extract data from source connection.
        
        Args:
            source_conn: Source connection configuration
            
        Returns:
            List of extracted records
        """
        if source_conn.connection_type == ConnectionType.MONGODB:
            return self._extract_from_mongodb(source_conn)
        else:
            raise NotImplementedError(f"Source type {source_conn.connection_type} not yet implemented")
    
    def _extract_from_mongodb(self, source_conn: Connection) -> List[Dict[str, Any]]:
        """
        Extract data from MongoDB using aggregation pipeline.
        
        Args:
            source_conn: MongoDB connection configuration
            
        Returns:
            List of extracted documents
        """
        client = pymongo.MongoClient(source_conn.connection_string)
        
        # Parse database and collection from table name
        db_name, collection_name = self._parse_mongo_table(self.job.source_table)
        collection = client[db_name][collection_name]
        
        # Build aggregation pipeline
        pipeline = self.job.aggregation_pipeline or []
        
        # Add limit for testing (remove in production)
        if not any("$limit" in stage for stage in pipeline):
            pipeline.append({"$limit": 1000})
        
        # Execute aggregation
        cursor = collection.aggregate(pipeline)
        documents = list(cursor)
        
        logger.info(f"Extracted {len(documents)} documents from MongoDB")
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
                
        return documents
    
    def _transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply transformations and masking to data.
        
        Args:
            data: Raw extracted data
            
        Returns:
            Transformed data
        """
        if not self.job.masking_config:
            return data
        
        # Apply masking configuration
        masked_data = []
        for record in data:
            masked_record = record.copy()
            
            for field, mask_type in self.job.masking_config.items():
                if field in masked_record:
                    if mask_type == "remove":
                        del masked_record[field]
                    elif mask_type == "hash":
                        masked_record[field] = "***MASKED***"
                    elif mask_type == "partial":
                        value = str(masked_record[field])
                        if len(value) > 4:
                            masked_record[field] = value[:2] + "***" + value[-2:]
                        else:
                            masked_record[field] = "***"
            
            masked_data.append(masked_record)
        
        logger.info(f"Applied masking to {len(masked_data)} records")
        return masked_data
    
    def _get_dlt_destination(self, dest_conn: Connection) -> str:
        """
        Get dlt destination string from connection configuration.
        
        Args:
            dest_conn: Destination connection configuration
            
        Returns:
            dlt destination string
        """
        if dest_conn.connection_type == ConnectionType.POSTGRES:
            return "postgres"
        elif dest_conn.connection_type == ConnectionType.BIGQUERY:
            return "bigquery"
        else:
            return "duckdb"  # Fallback for testing
    
    def _get_dataset_name(self) -> str:
        """
        Generate dataset name for the pipeline.
        
        Returns:
            Dataset name
        """
        return f"etl_job_{self.job.id}"
    
    def _parse_mongo_table(self, table_name: str) -> tuple:
        """
        Parse MongoDB database.collection format.
        
        Args:
            table_name: Table name in format "database.collection"
            
        Returns:
            Tuple of (database, collection)
        """
        if "." in table_name:
            return table_name.split(".", 1)
        else:
            return "test", table_name  # Default database