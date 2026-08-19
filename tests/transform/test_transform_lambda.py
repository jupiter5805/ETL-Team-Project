from unittest.mock import call, patch

from src.transformation.lambda_function import lambda_handler


ENVIRONMENT = {
    "INGESTION_BUCKET_NAME": "test-ingestion-bucket",
    "PROCESSED_BUCKET_NAME": "test-processed-bucket",
}


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_currency")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_lambda_handler_transforms_currency(
    mock_read,
    mock_transform,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/currency/test.json"
                }
            }
        }]
    }

    raw_data = [{
        "currency_id": 1,
        "currency_code": "GBP",
    }]

    transformed_data = [{
        "currency_id": 1,
        "currency_code": "GBP",
        "currency_name": "Pound Sterling",
    }]

    mock_read.return_value = raw_data
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_currency/test.parquet"

    result = lambda_handler(event, None)

    mock_read.assert_called_once_with(
        "test-ingestion-bucket",
        "raw/currency/test.json",
    )

    mock_transform.assert_called_once_with(raw_data)

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_currency.parquet",
    )

    mock_upload.assert_called_once_with(
        "/tmp/dim_currency.parquet",
        "dim_currency",
        "test-processed-bucket",
    )

    assert result["uploaded_file"] == "dim_currency/test.parquet"


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_design")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_lambda_handler_transforms_design(
    mock_read,
    mock_transform,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/design/test.json"
                }
            }
        }]
    }

    raw_data = [{"design_id": 1}]
    transformed_data = [{"design_id": 1}]

    mock_read.return_value = raw_data
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_design/test.parquet"

    result = lambda_handler(event, None)

    mock_read.assert_called_once_with(
        "test-ingestion-bucket",
        "raw/design/test.json",
    )

    mock_transform.assert_called_once_with(raw_data)

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_design.parquet",
    )

    mock_upload.assert_called_once_with(
        "/tmp/dim_design.parquet",
        "dim_design",
        "test-processed-bucket",
    )

    assert result["uploaded_file"] == "dim_design/test.parquet"


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_location")
@patch("src.transformation.lambda_function.read_current_table_state")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_lambda_handler_transforms_address(
    mock_exact_read,
    mock_current_state,
    mock_transform,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/address/test.json"
                }
            }
        }]
    }

    raw_data = [{"address_id": 1}]
    transformed_data = [{"location_id": 1}]

    mock_exact_read.return_value = raw_data

    # No counterparty data yet, so only dim_location is produced.
    mock_current_state.return_value = []

    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_location/test.parquet"

    result = lambda_handler(event, None)

    mock_exact_read.assert_called_once_with(
        "test-ingestion-bucket",
        "raw/address/test.json",
    )

    mock_transform.assert_called_once_with(raw_data)

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_location.parquet",
    )

    mock_upload.assert_called_once_with(
        "/tmp/dim_location.parquet",
        "dim_location",
        "test-processed-bucket",
    )

    mock_current_state.assert_called_once_with(
        "test-ingestion-bucket",
        "counterparty",
        "counterparty_id",
    )

    assert result["uploaded_file"] == "dim_location/test.parquet"


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_counterparty")
@patch("src.transformation.lambda_function.transform_location")
@patch("src.transformation.lambda_function.read_current_table_state")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_address_change_refreshes_dim_counterparty(
    mock_exact_read,
    mock_current_state,
    mock_transform_location,
    mock_transform_counterparty,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/address/test.json"
                }
            }
        }]
    }

    changed_address_data = [
        {
            "address_id": 10,
            "city": "Manchester",
        }
    ]

    location_data = [
        {
            "location_id": 10,
            "city": "Manchester",
        }
    ]

    counterparty_data = [
        {
            "counterparty_id": 1,
            "legal_address_id": 10,
        }
    ]

    current_address_data = [
        {
            "address_id": 10,
            "city": "Manchester",
        }
    ]

    counterparty_dimension_data = [
        {
            "counterparty_id": 1,
            "counterparty_legal_city": "Manchester",
        }
    ]

    mock_exact_read.return_value = changed_address_data

    mock_current_state.side_effect = [
        counterparty_data,
        current_address_data,
    ]

    mock_transform_location.return_value = location_data

    mock_transform_counterparty.return_value = (
        counterparty_dimension_data
    )

    mock_upload.side_effect = [
        "dim_location/test.parquet",
        "dim_counterparty/test.parquet",
    ]

    result = lambda_handler(event, None)

    mock_exact_read.assert_called_once_with(
        "test-ingestion-bucket",
        "raw/address/test.json",
    )

    mock_current_state.assert_has_calls([
        call(
            "test-ingestion-bucket",
            "counterparty",
            "counterparty_id",
        ),
        call(
            "test-ingestion-bucket",
            "address",
            "address_id",
        ),
    ])

    mock_transform_location.assert_called_once_with(
        changed_address_data,
    )

    mock_transform_counterparty.assert_called_once_with(
        counterparty_data,
        current_address_data,
    )

    assert mock_create_parquet.call_count == 2

    mock_create_parquet.assert_has_calls([
        call(
            location_data,
            "/tmp/dim_location.parquet",
        ),
        call(
            counterparty_dimension_data,
            "/tmp/dim_counterparty.parquet",
        ),
    ])

    assert mock_upload.call_count == 2

    assert result["uploaded_file"] == (
        "dim_location/test.parquet"
    )

    assert result["counterparty_uploaded_file"] == (
        "dim_counterparty/test.parquet"
    )


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_date")
@patch("src.transformation.lambda_function.transform_sales_order")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_lambda_handler_transforms_sales_order(
    mock_read,
    mock_transform_sales,
    mock_transform_date,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/sales_order/test.json"
                }
            }
        }]
    }

    raw_data = [{"sales_order_id": 1}]
    transformed_data = [{"sales_order_id": 1}]
    date_data = [{"date_id": "2026-08-18"}]

    mock_read.return_value = raw_data
    mock_transform_sales.return_value = transformed_data
    mock_transform_date.return_value = date_data

    mock_upload.side_effect = [
        "fact_sales_order/test.parquet",
        "dim_date/test.parquet",
    ]

    result = lambda_handler(event, None)

    mock_read.assert_called_once_with(
        "test-ingestion-bucket",
        "raw/sales_order/test.json",
    )

    mock_transform_sales.assert_called_once_with(raw_data)
    mock_transform_date.assert_called_once_with(raw_data)

    assert mock_create_parquet.call_count == 2

    mock_create_parquet.assert_has_calls([
        call(
            transformed_data,
            "/tmp/fact_sales_order.parquet",
        ),
        call(
            date_data,
            "/tmp/dim_date.parquet",
        ),
    ])

    assert mock_upload.call_count == 2

    assert result["uploaded_file"] == (
        "fact_sales_order/test.parquet"
    )


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_staff")
@patch("src.transformation.lambda_function.read_current_table_state")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_lambda_handler_transforms_staff(
    mock_exact_read,
    mock_current_state,
    mock_transform,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/staff/test.json"
                }
            }
        }]
    }

    staff_data = [
        {
            "staff_id": 1,
            "department_id": 2,
        }
    ]

    department_data = [
        {
            "department_id": 2,
            "department_name": "Purchasing",
        }
    ]

    transformed_data = [{"staff_id": 1}]

    mock_exact_read.return_value = staff_data
    mock_current_state.return_value = department_data
    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_staff/test.parquet"

    result = lambda_handler(event, None)

    mock_exact_read.assert_called_once_with(
        "test-ingestion-bucket",
        "raw/staff/test.json",
    )

    mock_current_state.assert_called_once_with(
        "test-ingestion-bucket",
        "department",
        "department_id",
    )

    mock_transform.assert_called_once_with(
        staff_data,
        department_data,
    )

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_staff.parquet",
    )

    assert result["uploaded_file"] == "dim_staff/test.parquet"


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_staff")
@patch("src.transformation.lambda_function.read_current_table_state")
def test_department_change_refreshes_dim_staff(
    mock_current_state,
    mock_transform,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/department/test.json"
                }
            }
        }]
    }

    staff_data = [
        {
            "staff_id": 1,
            "department_id": 2,
        }
    ]

    department_data = [
        {
            "department_id": 2,
            "department_name": "Commercial",
        }
    ]

    transformed_data = [
        {
            "staff_id": 1,
            "department_name": "Commercial",
        }
    ]

    mock_current_state.side_effect = [
        staff_data,
        department_data,
    ]

    mock_transform.return_value = transformed_data
    mock_upload.return_value = "dim_staff/test.parquet"

    result = lambda_handler(event, None)

    assert mock_current_state.call_count == 2

    mock_current_state.assert_has_calls([
        call(
            "test-ingestion-bucket",
            "staff",
            "staff_id",
        ),
        call(
            "test-ingestion-bucket",
            "department",
            "department_id",
        ),
    ])

    mock_transform.assert_called_once_with(
        staff_data,
        department_data,
    )

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_staff.parquet",
    )

    assert result["output_table"] == "dim_staff"


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.read_current_table_state")
def test_department_event_before_staff_is_safe(
    mock_current_state,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/department/test.json"
                }
            }
        }]
    }

    mock_current_state.return_value = []

    result = lambda_handler(event, None)

    assert result == {
        "table_name": "department",
        "status": "no_staff_data",
    }


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.transform_counterparty")
@patch("src.transformation.lambda_function.read_current_table_state")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_lambda_handler_transforms_counterparty(
    mock_exact_read,
    mock_current_state,
    mock_transform,
    mock_create_parquet,
    mock_upload,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/counterparty/test.json"
                }
            }
        }]
    }

    counterparty_data = [
        {
            "counterparty_id": 1,
            "legal_address_id": 10,
        }
    ]

    address_data = [
        {
            "address_id": 10,
        }
    ]

    transformed_data = [
        {
            "counterparty_id": 1,
        }
    ]

    mock_exact_read.return_value = counterparty_data
    mock_current_state.return_value = address_data
    mock_transform.return_value = transformed_data

    mock_upload.return_value = (
        "dim_counterparty/test.parquet"
    )

    result = lambda_handler(event, None)

    mock_exact_read.assert_called_once_with(
        "test-ingestion-bucket",
        "raw/counterparty/test.json",
    )

    mock_current_state.assert_called_once_with(
        "test-ingestion-bucket",
        "address",
        "address_id",
    )

    mock_transform.assert_called_once_with(
        counterparty_data,
        address_data,
    )

    mock_create_parquet.assert_called_once_with(
        transformed_data,
        "/tmp/dim_counterparty.parquet",
    )

    assert result["uploaded_file"] == (
        "dim_counterparty/test.parquet"
    )


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.read_current_table_state")
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_counterparty_event_before_address_is_safe(
    mock_exact_read,
    mock_current_state,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/counterparty/test.json"
                }
            }
        }]
    }

    mock_exact_read.return_value = [
        {
            "counterparty_id": 1,
            "legal_address_id": 10,
        }
    ]

    mock_current_state.return_value = []

    result = lambda_handler(event, None)

    assert result == {
        "table_name": "counterparty",
        "status": "no_address_data",
    }


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.read_table_data_from_s3")
def test_lambda_handler_raises_error(mock_read):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/currency/test.json"
                }
            }
        }]
    }

    mock_read.side_effect = Exception("S3 read failed")

    try:
        lambda_handler(event, None)
        assert False
    except Exception as error:
        assert str(error) == "S3 read failed"


@patch.dict("os.environ", ENVIRONMENT)
@patch("src.transformation.lambda_function.create_parquet")
@patch("src.transformation.lambda_function.upload_parquet_to_s3")
def test_lambda_handler_ignores_unsupported_table(
    mock_upload,
    mock_create_parquet,
):
    event = {
        "Records": [{
            "s3": {
                "object": {
                    "key": "raw/payment/test.json"
                }
            }
        }]
    }

    result = lambda_handler(event, None)

    assert result == {
        "table_name": "payment",
        "status": "ignored",
    }

    mock_create_parquet.assert_not_called()
    mock_upload.assert_not_called()
