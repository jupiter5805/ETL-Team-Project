import boto3
import json

from src.transformation.transform import transform_date
from src.transformation.write_parquet import (
    create_parquet,
    upload_parquet_to_s3
)


def read_latest_table_data(bucket_name, table_name):
    s3 = boto3.client("s3")

    prefix = f"{table_name}/"

    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix
    )

    objects = response["Contents"]

    latest_object = max(
        objects,
        key=lambda object: object["LastModified"]
    )

    response = s3.get_object(
        Bucket=bucket_name,
        Key=latest_object["Key"]
    )

    data = response["Body"].read()

    return json.loads(data)


if __name__ == "__main__":

    sales_order_data = read_latest_table_data(
        "marvel-etl-project-ingestion",
        "sales_order"
    )

    transformed_date = transform_date(sales_order_data)

    create_parquet(
        transformed_date,
        "dim_date.parquet"
    )

    uploaded_file = upload_parquet_to_s3(
        "dim_date.parquet",
        "dim_date",
        "marvel-etl-project-processed"
    )

    print("First 3 dates:")
    print(transformed_date[:3])

    print("Last 3 dates:")
    print(transformed_date[-3:])

    print(f"Total dates: {len(transformed_date)}")
    print(f"Uploaded to: {uploaded_file}")
