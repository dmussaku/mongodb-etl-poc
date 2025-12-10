


import dlt
from .dlt_config.mongodb.destination import mongo_sink
from .dlt_config.mongodb.source import mongodb_collection


def main():
    # ----- configure SOURCE -----
    SRC_URI = "mongodb://root:password@localhost:27017"
    SRC_DB = "university"
    SRC_COLLECTION = "people"

    # Aggregation pipeline to limit 10 documents
    aggregation_pipeline = [{"$limit": 100}]

    source_data = mongodb_collection(
        connection_url=SRC_URI,
        database=SRC_DB,
        collection=SRC_COLLECTION,
        aggregation_pipeline=aggregation_pipeline,
        write_disposition="replace",   # affects how dlt *conceptually* handles table
    )

    # ----- configure DESTINATION -----
    DEST_URI = "mongodb://root:password@localhost:27017"
    DEST_DB = "analytics"
    DEST_COLLECTION = "people_100"

    # You can parametrize the destination by calling it with kwargs
    dest = mongo_sink(
        connection_url=DEST_URI,
        database=DEST_DB,
        collection=DEST_COLLECTION,
    )

    pipeline = dlt.pipeline(
        pipeline_name="university_people_etl",
        destination=dest,       # custom destination instance
        dataset_name="ignored", # not used by our custom sink
        dev_mode=True,
    )

    load_info = pipeline.run(source_data)
    print(load_info)


if __name__ == "__main__":
    main()