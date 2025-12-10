from typing import Optional
import dlt
from pymongo import MongoClient


@dlt.destination(
    name="mongo_destination",
    batch_size=1_000,  # items is a list[dict]
    loader_file_format="typed-jsonl",  # dlt writes JSONL, we get Python dicts here
    max_table_nesting=0,
    skip_dlt_columns_and_tables=True,
)
def mongo_sink(
    items,
    table,  # table schema (we mostly use table["name"])
    connection_url: str = dlt.secrets.value,
    database: str = dlt.config.value,
    collection: Optional[str] = None,
) -> None:
    """
    Custom Mongo destination.

    You can parametrize it via:
      - connection_url
      - database
      - collection (fallback: table["name"])
    """
    if not items:
        return

    client = MongoClient(connection_url, uuidRepresentation="standard", tz_aware=True)
    db = client[database]

    coll_name = collection or table["name"]
    coll = db[coll_name]

    # items is a list of dicts
    coll.insert_many(list(items))
