import boto3
import json

from src.transformation.transform import transform_staff
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

    staff_data = read_latest_table_data(
        "marvel-etl-project-ingestion",
        "staff"
    )

    department_data = read_latest_table_data(
        "marvel-etl-project-ingestion",
        "department"
    )

    transformed_staff = transform_staff(
        staff_data,
        department_data
    )

    create_parquet(
        transformed_staff,
        "dim_staff.parquet"
    )

    uploaded_file = upload_parquet_to_s3(
        "dim_staff.parquet",
        "dim_staff",
        "marvel-etl-project-processed"
    )

    print(transformed_staff)
    print(f"Uploaded to: {uploaded_file}")
