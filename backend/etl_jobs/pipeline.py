import dlt
import logging
from typing import Dict, Any
from .dlt_config import (
    SourceType,
    DestinationType,
    get_source_factory,
    get_destination_factory,
)

logger = logging.getLogger(__name__)


def run_pipeline(
    source_config: Dict[str, Any],
    destination_config: Dict[str, Any],
    pipeline_name: str = "etl_pipeline",
    dev_mode: bool = True,
):
    """
    Run an extensible ETL pipeline supporting multiple sources and destinations.

    Args:
        source_config: Source configuration dictionary with 'type' and type-specific parameters
        destination_config: Destination configuration dictionary with 'type' and type-specific parameters
        pipeline_name: Name of the DLT pipeline
        dev_mode: Whether to run in development mode

    Source Config Examples:
        MongoDB: {
            "type": "mongodb",
            "connection_url": "mongodb://user:pass@host:port",
            "database": "db_name",
            "collection": "collection_name",
            "aggregation_pipeline": [{"$limit": 100}],  # optional
            "query": {"field": "value"},  # optional, ignored if aggregation_pipeline provided
            "write_disposition": "replace"  # optional
        }

        Future PostgreSQL: {
            "type": "postgresql",
            "connection_url": "postgresql://user:pass@host:port/db",
            "table": "table_name",
            "query": "SELECT * FROM table WHERE condition"
        }

    Destination Config Examples:
        MongoDB: {
            "type": "mongodb",
            "connection_url": "mongodb://user:pass@host:port",
            "database": "db_name",
            "collection": "collection_name"
        }

        Future S3: {
            "type": "s3",
            "bucket": "bucket_name",
            "path": "data/output/",
            "format": "parquet"
        }

    Returns:
        Load info from DLT pipeline execution

    Raises:
        ValueError: If source or destination type is not supported
    """
    logger.info(f"Starting pipeline '{pipeline_name}' with source_config: {source_config}, destination_config: {destination_config}, dev_mode: {dev_mode}")
    
    # Validate and get source type
    source_type_str = source_config.get("type")
    if not source_type_str:
        raise ValueError("Source config must include 'type' field")

    try:
        source_type = SourceType(source_type_str)
    except ValueError:
        supported_sources = [t.value for t in SourceType]
        raise ValueError(
            f"Unsupported source type '{source_type_str}'. Supported: {supported_sources}"
        )

    # Validate and get destination type
    dest_type_str = destination_config.get("type")
    if not dest_type_str:
        raise ValueError("Destination config must include 'type' field")

    try:
        dest_type = DestinationType(dest_type_str)
    except ValueError:
        supported_destinations = [t.value for t in DestinationType]
        raise ValueError(
            f"Unsupported destination type '{dest_type_str}'. Supported: {supported_destinations}"
        )

    # Get source factory and create source
    try:
        source_factory = get_source_factory(source_type)
        source_data = source_factory(source_config)
    except ValueError as e:
        raise ValueError(f"Source error: {e}")
    except NotImplementedError as e:
        raise ValueError(f"Source type '{source_type.value}' not implemented yet: {e}")

    # Get destination factory and create destination
    try:
        dest_factory = get_destination_factory(dest_type)
        destination = dest_factory(destination_config)
    except ValueError as e:
        raise ValueError(f"Destination error: {e}")
    except NotImplementedError as e:
        raise ValueError(
            f"Destination type '{dest_type.value}' not implemented yet: {e}"
        )

    # Create and run pipeline
    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=destination,
        dataset_name="ignored",  # may be used by some destinations
        dev_mode=dev_mode,
    )

    load_info = pipeline.run(source_data)
    logger.info(f"Load info type: {type(load_info)}")
    logger.info(f"Load info attributes: {dir(load_info)}")
    logger.info(f"Load info string representation: {str(load_info)}")
    return load_info
