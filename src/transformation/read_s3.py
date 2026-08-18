import boto3
import json

from src.transformation.transform import transform_sales_order
from src.transformation.write_parquet import (
    create_parquet,
    upload_parquet_to_s3
)


def read_latest_table_data(bucket_name, table_name):
    s3 = boto3.client("s3")

    prefix = f"raw/{table_name}/"

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

    transformed_sales_orders = transform_sales_order(
        sales_order_data
    )

    create_parquet(
        transformed_sales_orders,
        "fact_sales_order.parquet"
    )

    uploaded_file = upload_parquet_to_s3(
        "fact_sales_order.parquet",
        "fact_sales_order",
        "marvel-etl-project-processed"
    )

    print("First 3 transformed sales orders:")
    print(transformed_sales_orders[:3])

    print(f"Total sales orders: {len(transformed_sales_orders)}")

    print(f"Uploaded to: {uploaded_file}")
