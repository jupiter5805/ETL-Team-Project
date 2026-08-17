import boto3
import pandas as pd
from datetime import datetime


def create_parquet(data, file_name):
    dataframe = pd.DataFrame(data)

    dataframe.to_parquet(
        file_name,
        index=False
    )


def upload_parquet_to_s3(file_name, table_name, bucket_name):
    s3 = boto3.client("s3")

    current_time = datetime.now().isoformat()

    object_key = f"{table_name}/{current_time}.parquet"

    s3.upload_file(
        file_name,
        bucket_name,
        object_key
    )

    return object_key
