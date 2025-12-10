"""
Factory functions and registry for data sources and destinations.
"""

import logging
from typing import Dict, Any
from .types import SourceType, DestinationType

logger = logging.getLogger(__name__)


def _get_mongodb_source(config: Dict[str, Any]) -> Any:
    """Configure MongoDB source"""
    logger.info(f"Creating MongoDB source with config: {config}")
    from .mongodb.source import mongodb_collection

    return mongodb_collection(
        connection_url=config["connection_url"],
        database=config["database"],
        collection=config["collection"],
        aggregation_pipeline=config.get("aggregation_pipeline"),
        query=config.get("query"),
        write_disposition=config.get("write_disposition", "append"),
    )


def _get_mongodb_destination(config: Dict[str, Any]) -> Any:
    """Configure MongoDB destination"""
    logger.info(f"Creating MongoDB destination with config: {config}")
    from .mongodb.destination import mongo_sink

    return mongo_sink(
        connection_url=config["connection_url"],
        database=config["database"],
        collection=config["collection"],
    )


# Future source factories can be added here
def _get_postgresql_source(config: Dict[str, Any]) -> Any:
    """Configure PostgreSQL source (placeholder for future implementation)"""
    logger.info(f"Attempting to create PostgreSQL source with config: {config}")
    raise NotImplementedError("PostgreSQL source not implemented yet")


def _get_api_source(config: Dict[str, Any]) -> Any:
    """Configure API source (placeholder for future implementation)"""
    logger.info(f"Attempting to create API source with config: {config}")
    raise NotImplementedError("API source not implemented yet")


# Future destination factories can be added here
def _get_postgresql_destination(config: Dict[str, Any]) -> Any:
    """Configure PostgreSQL destination (placeholder for future implementation)"""
    logger.info(f"Attempting to create PostgreSQL destination with config: {config}")
    raise NotImplementedError("PostgreSQL destination not implemented yet")


def _get_s3_destination(config: Dict[str, Any]) -> Any:
    """Configure S3 destination (placeholder for future implementation)"""
    logger.info(f"Attempting to create S3 destination with config: {config}")
    raise NotImplementedError("S3 destination not implemented yet")


# Registry for source and destination factories
SOURCE_FACTORIES = {
    SourceType.MONGODB: _get_mongodb_source,
    SourceType.POSTGRESQL: _get_postgresql_source,
    SourceType.API: _get_api_source,
    # Additional sources can be registered here
}

DESTINATION_FACTORIES = {
    DestinationType.MONGODB: _get_mongodb_destination,
    DestinationType.POSTGRESQL: _get_postgresql_destination,
    DestinationType.S3: _get_s3_destination,
    # Additional destinations can be registered here
}


def get_source_factory(source_type: SourceType):
    """Get the factory function for a source type"""
    logger.info(f"Getting source factory for type: {source_type}")
    factory = SOURCE_FACTORIES.get(source_type)
    if not factory:
        raise ValueError(f"Source type '{source_type.value}' not registered")
    return factory


def get_destination_factory(destination_type: DestinationType):
    """Get the factory function for a destination type"""
    logger.info(f"Getting destination factory for type: {destination_type}")
    factory = DESTINATION_FACTORIES.get(destination_type)
    if not factory:
        raise ValueError(f"Destination type '{destination_type.value}' not registered")
    return factory
