import logging
import os
from urllib.parse import unquote_plus

from .read_s3 import (
    read_current_table_state,
    read_table_data_from_s3,
)
from .transform import (
    transform_currency,
    transform_design,
    transform_location,
    transform_staff,
    transform_counterparty,
    transform_date,
    transform_sales_order,
)
from .write_parquet import (
    create_parquet,
    upload_parquet_to_s3,
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        ingestion_bucket = os.environ["INGESTION_BUCKET_NAME"]
        processed_bucket = os.environ["PROCESSED_BUCKET_NAME"]

        logger.info("Transformation Lambda started")

        object_key = unquote_plus(
            event["Records"][0]["s3"]["object"]["key"]
        )

        table_name = object_key.split("/")[1]

        logger.info("Processing file: %s", object_key)
        logger.info("Source table: %s", table_name)

        if table_name == "currency":
            data = read_table_data_from_s3(
                ingestion_bucket,
                object_key,
            )

            transformed_data = transform_currency(data)
            output_table = "dim_currency"

        elif table_name == "design":
            data = read_table_data_from_s3(
                ingestion_bucket,
                object_key,
            )

            transformed_data = transform_design(data)
            output_table = "dim_design"

        elif table_name == "address":
            data = read_table_data_from_s3(
                ingestion_bucket,
                object_key,
            )

            transformed_data = transform_location(data)
            output_table = "dim_location"

        elif table_name == "sales_order":
            data = read_table_data_from_s3(
                ingestion_bucket,
                object_key,
            )

            transformed_data = transform_sales_order(data)
            transformed_date_data = transform_date(data)

            output_table = "fact_sales_order"
            date_output_table = "dim_date"

        elif table_name == "staff":
            staff_data = read_table_data_from_s3(
                ingestion_bucket,
                object_key,
            )

            department_data = read_current_table_state(
                ingestion_bucket,
                "department",
                "department_id",
            )

            transformed_data = transform_staff(
                staff_data,
                department_data,
            )

            output_table = "dim_staff"

        elif table_name == "department":
            staff_data = read_current_table_state(
                ingestion_bucket,
                "staff",
                "staff_id",
            )

            if not staff_data:
                logger.info(
                    "No staff data available yet for department update"
                )

                return {
                    "table_name": table_name,
                    "status": "no_staff_data",
                }

            department_data = read_current_table_state(
                ingestion_bucket,
                "department",
                "department_id",
            )

            transformed_data = transform_staff(
                staff_data,
                department_data,
            )

            output_table = "dim_staff"

        elif table_name == "counterparty":
            counterparty_data = read_table_data_from_s3(
                ingestion_bucket,
                object_key,
            )

            address_data = read_current_table_state(
                ingestion_bucket,
                "address",
                "address_id",
            )

            if not address_data:
                logger.info(
                    "No address data available yet "
                    "for counterparty update"
                )

                return {
                    "table_name": table_name,
                    "status": "no_address_data",
                }

            transformed_data = transform_counterparty(
                counterparty_data,
                address_data,
            )

            output_table = "dim_counterparty"

        else:
            logger.info(
                "Ignoring unsupported table: %s",
                table_name,
            )

            return {
                "table_name": table_name,
                "status": "ignored",
            }

        # AWS Lambda provides /tmp as writable temporary storage.
        file_name = f"/tmp/{output_table}.parquet"  # nosec B108

        create_parquet(
            transformed_data,
            file_name,
        )

        uploaded_file = upload_parquet_to_s3(
            file_name,
            output_table,
            processed_bucket,
        )

        logger.info(
            "Uploaded transformed file: %s",
            uploaded_file,
        )

        result = {
            "table_name": table_name,
            "output_table": output_table,
            "uploaded_file": uploaded_file,
        }

        if table_name == "sales_order":
            # AWS Lambda provides /tmp as writable temporary storage.
            date_file_name = "/tmp/dim_date.parquet"  # nosec B108

            create_parquet(
                transformed_date_data,
                date_file_name,
            )

            date_uploaded_file = upload_parquet_to_s3(
                date_file_name,
                date_output_table,
                processed_bucket,
            )

            logger.info(
                "Uploaded date file: %s",
                date_uploaded_file,
            )

        if table_name == "address":
            counterparty_data = read_current_table_state(
                ingestion_bucket,
                "counterparty",
                "counterparty_id",
            )

            if counterparty_data:
                current_address_data = read_current_table_state(
                    ingestion_bucket,
                    "address",
                    "address_id",
                )

                transformed_counterparty_data = (
                    transform_counterparty(
                        counterparty_data,
                        current_address_data,
                    )
                )

                # AWS Lambda provides /tmp as writable temporary storage.
                counterparty_file_name = (
                    "/tmp/dim_counterparty.parquet"  # nosec B108
                )

                create_parquet(
                    transformed_counterparty_data,
                    counterparty_file_name,
                )

                counterparty_uploaded_file = (
                    upload_parquet_to_s3(
                        counterparty_file_name,
                        "dim_counterparty",
                        processed_bucket,
                    )
                )

                logger.info(
                    "Refreshed dim_counterparty: %s",
                    counterparty_uploaded_file,
                )

                result["counterparty_uploaded_file"] = (
                    counterparty_uploaded_file
                )

        return result

    except Exception:
        logger.exception("Transformation Lambda failed")
        raise
