import logging
from urllib.parse import unquote_plus

from .connect_RDS import get_connection
from .reader import read_parquet_from_s3
from .loader import (
    load_staff,
    load_location,
    load_design,
    load_currency,
    load_counterparty,
    load_date,
    load_sales_order,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


LOADERS = {
    "dim_staff": load_staff,
    "dim_location": load_location,
    "dim_design": load_design,
    "dim_currency": load_currency,
    "dim_counterparty": load_counterparty,
    "dim_date": load_date,
    "fact_sales_order": load_sales_order,
}


def lambda_handler(event, context):
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]

    object_key = unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )

    table_name = object_key.split("/", 1)[0]

    if table_name not in LOADERS:
        raise ValueError(
            f"Unsupported table: {table_name}"
        )

    logger.info(
        "Loading %s from s3://%s/%s",
        table_name,
        bucket_name,
        object_key,
    )

    dataframe = read_parquet_from_s3(
        bucket_name,
        object_key,
    )

    records = dataframe.to_dict(
        orient="records"
    )

    loader_function = LOADERS[table_name]

    connection = get_connection()

    try:
        with connection.cursor() as cur:
            loader_function(
                cur,
                records,
            )

        connection.commit()

        logger.info(
            "Successfully loaded %d rows into %s",
            len(records),
            table_name,
        )

    except Exception:
        connection.rollback()

        logger.exception(
            "Failed loading %s",
            table_name,
        )

        raise

    finally:
        connection.close()

    return {
        "table_name": table_name,
        "object_key": object_key,
        "rows_loaded": len(records),
    }
