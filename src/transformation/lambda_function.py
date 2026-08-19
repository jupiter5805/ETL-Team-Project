import logging
import os

from src.transformation.read_s3 import read_latest_table_data
from src.transformation.transform import (
    transform_currency,
    transform_design,
    transform_location,
    transform_staff,
    transform_counterparty,
    transform_date,
    transform_sales_order
)
from src.transformation.write_parquet import (
    create_parquet,
    upload_parquet_to_s3
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    ingestion_bucket = os.environ["INGESTION_BUCKET_NAME"]
    processed_bucket = os.environ["PROCESSED_BUCKET_NAME"]

    logger.info("Transformation Lambda started")

    object_key = event["Records"][0]["s3"]["object"]["key"]
    table_name = object_key.split("/")[1]

    if table_name == "currency":
        data = read_latest_table_data(
            ingestion_bucket,
            "currency"
        )
        transformed_data = transform_currency(data)
        output_table = "dim_currency"

    elif table_name == "design":
        data = read_latest_table_data(
            ingestion_bucket,
            "design"
        )
        transformed_data = transform_design(data)
        output_table = "dim_design"

    elif table_name == "address":
        data = read_latest_table_data(
            ingestion_bucket,
            "address"
        )
        transformed_data = transform_location(data)
        output_table = "dim_location"

    elif table_name == "sales_order":
        data = read_latest_table_data(
            ingestion_bucket,
            "sales_order"
        )

        transformed_data = transform_sales_order(data)
        transformed_date_data = transform_date(data)

        output_table = "fact_sales_order"
        date_output_table = "dim_date"

    elif table_name == "staff":
        staff_data = read_latest_table_data(
            ingestion_bucket,
            "staff"
        )

        department_data = read_latest_table_data(
            ingestion_bucket,
            "department"
        )

        transformed_data = transform_staff(
            staff_data,
            department_data
        )

        output_table = "dim_staff"

    elif table_name == "counterparty":
        counterparty_data = read_latest_table_data(
            ingestion_bucket,
            "counterparty"
        )

        address_data = read_latest_table_data(
            ingestion_bucket,
            "address"
        )

        transformed_data = transform_counterparty(
            counterparty_data,
            address_data
        )

        output_table = "dim_counterparty"

    file_name = f"/tmp/{output_table}.parquet"

    create_parquet(
        transformed_data,
        file_name
    )

    uploaded_file = upload_parquet_to_s3(
        file_name,
        output_table,
        processed_bucket
    )

    if table_name == "sales_order":
        date_file_name = "/tmp/dim_date.parquet"

        create_parquet(
            transformed_date_data,
            date_file_name
        )

        upload_parquet_to_s3(
            date_file_name,
            date_output_table,
            processed_bucket
        )

    return {
        "table_name": table_name,
        "output_table": output_table,
        "uploaded_file": uploaded_file
    }