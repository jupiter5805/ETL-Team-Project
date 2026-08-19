from unittest.mock import patch

from src.transformation.lambda_function import lambda_handler


@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_currency")
@patch("src.transformation.lambda_function.read_latest_table_data")
def test_lambda_handler_transforms_currency(
    mock_read,
    mock_transform,
    mock_create_parquet,
    mock_upload
):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/currency/test.json"}
            }
        }]
    }

    raw_data = [{
        "currency_id": 1,
        "currency_code": "GBP"
    }]

    transformed_data = [{
        "currency_id": 1,
        "currency_code": "GBP",
        "currency_name": "Pound Sterling"
    }]

    mock_read.return_value = raw_data
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_currency/test.parquet"

    result = lambda_handler(event, None)

    mock_read.assert_called_once_with(
        "test-ingestion-bucket",
        "currency"
    )
    mock_transform.assert_called_once_with(raw_data)

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_currency.parquet"
    )

    mock_upload.assert_called_once_with(
        "/tmp/dim_currency.parquet",
        "dim_currency",
        "test-processed-bucket"
    )

    assert result["uploaded_file"] == "dim_currency/test.parquet"


@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_design")
@patch("src.transformation.lambda_function.read_latest_table_data")
def test_lambda_handler_transforms_design(
    mock_read,
    mock_transform,
    mock_create_parquet,
    mock_upload
):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/design/test.json"}
            }
        }]
    }

    raw_data = [{"design_id": 1}]
    transformed_data = [{"design_id": 1}]

    mock_read.return_value = raw_data
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_design/test.parquet"

    result = lambda_handler(event, None)

    mock_transform.assert_called_once_with(raw_data)

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_design.parquet"
    )

    mock_upload.assert_called_once_with(
        "/tmp/dim_design.parquet",
        "dim_design",
        "test-processed-bucket"
    )

    assert result["uploaded_file"] == "dim_design/test.parquet"


@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_location")
@patch("src.transformation.lambda_function.read_latest_table_data")
def test_lambda_handler_transforms_address(
    mock_read,
    mock_transform,
    mock_create_parquet,
    mock_upload
):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/address/test.json"}
            }
        }]
    }

    raw_data = [{"address_id": 1}]
    transformed_data = [{"location_id": 1}]

    mock_read.return_value = raw_data
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_location/test.parquet"

    result = lambda_handler(event, None)

    mock_transform.assert_called_once_with(raw_data)

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_location.parquet"
    )

    mock_upload.assert_called_once_with(
        "/tmp/dim_location.parquet",
        "dim_location",
        "test-processed-bucket"
    )

    assert result["uploaded_file"] == "dim_location/test.parquet"


@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_date")
@patch("src.transformation.lambda_function.transform_sales_order")
@patch("src.transformation.lambda_function.read_latest_table_data")
def test_lambda_handler_transforms_sales_order(
    mock_read,
    mock_transform_sales,
    mock_transform_date,
    mock_create_parquet,
    mock_upload
):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/sales_order/test.json"}
            }
        }]
    }

    raw_data = [{"sales_order_id": 1}]
    transformed_data = [{"sales_order_id": 1}]
    date_data = [{"date_id": "2026-08-18"}]

    mock_read.return_value = raw_data
    mock_transform_sales.return_value = transformed_data
    mock_transform_date.return_value = date_data
    mock_upload.return_value = "fact_sales_order/test.parquet"

    result = lambda_handler(event, None)

    mock_transform_sales.assert_called_once_with(raw_data)
    mock_transform_date.assert_called_once_with(raw_data)

    assert mock_create_parquet.call_count == 2
    assert mock_upload.call_count == 2

    mock_create_parquet.assert_any_call(
        transformed_data,
        "/tmp/fact_sales_order.parquet"
    )

    mock_create_parquet.assert_any_call(
        date_data,
        "/tmp/dim_date.parquet"
    )

    assert result["uploaded_file"] == "fact_sales_order/test.parquet"


@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_staff")
@patch("src.transformation.lambda_function.read_latest_table_data")
def test_lambda_handler_transforms_staff(
    mock_read,
    mock_transform,
    mock_create_parquet,
    mock_upload
):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/staff/test.json"}
            }
        }]
    }

    staff_data = [{"staff_id": 1}]
    department_data = [{"department_id": 2}]
    transformed_data = [{"staff_id": 1}]

    mock_read.side_effect = [staff_data, department_data]
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_staff/test.parquet"

    result = lambda_handler(event, None)

    mock_transform.assert_called_once_with(
        staff_data,
        department_data
    )

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_staff.parquet"
    )

    assert result["uploaded_file"] == "dim_staff/test.parquet"


@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_counterparty")
@patch("src.transformation.lambda_function.read_latest_table_data")
def test_lambda_handler_transforms_counterparty(
    mock_read,
    mock_transform,
    mock_create_parquet,
    mock_upload
):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/counterparty/test.json"}
            }
        }]
    }

    counterparty_data = [{"counterparty_id": 1}]
    address_data = [{"address_id": 10}]
    transformed_data = [{"counterparty_id": 1}]

    mock_read.side_effect = [counterparty_data, address_data]
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_counterparty/test.parquet"

    result = lambda_handler(event, None)

    mock_transform.assert_called_once_with(
        counterparty_data,
        address_data
    )

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_counterparty.parquet"
    )

    assert result["uploaded_file"] == "dim_counterparty/test.parquet"


@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.read_latest_table_data")
def test_lambda_handler_raises_error(mock_read):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/currency/test.json"}
            }
        }]
    }

    mock_read.side_effect = Exception("S3 read failed")

    try:
        lambda_handler(event, None)
        assert False
    except Exception as error:
        assert str(error) == "S3 read failed"

@patch.dict("os.environ", {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket"
})
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
def test_lambda_handler_ignores_unsupported_table(mock_upload, mock_create_parquet):
    event = {
        "Records": [{
            "s3": {
                "object": {"key": "raw/payment/test.json"}
            }
        }]
    }

    result = lambda_handler(event, None)

    assert result == {"table_name": "payment", "status": "ignored"}
    mock_create_parquet.assert_not_called()
    mock_upload.assert_not_called()