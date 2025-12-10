from itertools import islice
from typing import Any, Dict, Iterator, Optional
from bson.decimal128 import Decimal128
from bson.objectid import ObjectId

import dlt
from pymongo import MongoClient
from dlt.common.time import ensure_pendulum_datetime_utc
from dlt.common.typing import TDataItem
from dlt.common.utils import map_nested_values_in_place

CHUNK_SIZE = 10_000


@dlt.source(max_table_nesting=0)  # no nested subtables unless you want them
def mongodb_collection(
    connection_url: str = dlt.secrets.value,
    database: Optional[str] = dlt.config.value,
    collection: str = dlt.config.value,
    query: Optional[Dict[str, Any]] = None,
    aggregation_pipeline: Optional[list] = None,
    write_disposition: Optional[str] = dlt.config.value,
) -> Any:
    client: Any = MongoClient(
        connection_url, uuidRepresentation="standard", tz_aware=True
    )

    mongo_database = client.get_default_database() if not database else client[database]
    collection_obj = mongo_database[collection]

    def collection_documents(
        client: Any,
        collection: Any,
        query: Optional[Dict[str, Any]] = None,
        aggregation_pipeline: Optional[list] = None,
    ) -> Iterator[TDataItem]:
        loader = CollectionLoader(
            client,
            collection,
            query=query or {},
            aggregation_pipeline=aggregation_pipeline,
        )
        yield from loader.load_documents()

    return dlt.resource(  # type: ignore
        collection_documents,
        name=collection_obj.name,  # table/collection name
        primary_key="_id",
        write_disposition=write_disposition,
    )(client, collection_obj, query=query, aggregation_pipeline=aggregation_pipeline)


class CollectionLoader:
    def __init__(
        self,
        client: Any,
        collection: Any,
        query: Dict[str, Any],
        aggregation_pipeline: Optional[list] = None,
    ) -> None:
        self.client = client
        self.collection = collection
        self.query = query
        self.aggregation_pipeline = aggregation_pipeline

    def load_documents(self) -> Iterator[TDataItem]:
        if self.aggregation_pipeline:
            # Use aggregation pipeline if provided
            cursor = self.collection.aggregate(self.aggregation_pipeline)
        else:
            # Fall back to regular find query
            cursor = self.collection.find(self.query)

        while docs_slice := list(islice(cursor, CHUNK_SIZE)):
            # convert ObjectId / Decimal / datetimes to JSON-friendly values
            yield map_nested_values_in_place(convert_mongo_objs, docs_slice)


def convert_mongo_objs(value: Any) -> Any:
    if isinstance(value, (ObjectId, Decimal128)):
        return str(value)
    # Handle datetime objects
    try:
        import pendulum

        if isinstance(value, pendulum.DateTime):
            return ensure_pendulum_datetime_utc(value)
    except ImportError:
        pass
    # Handle standard datetime objects
    from datetime import datetime

    if isinstance(value, datetime):
        return ensure_pendulum_datetime_utc(value)
    return value
