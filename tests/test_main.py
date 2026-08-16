from unittest.mock import patch

from src.ingestion.main import lambda_handler


def test_lambda_handler():
    with patch("src.ingestion.main.get_totesys_connection") as mock_connection:
        with patch("src.ingestion.main.extract_all_tables") as mock_extract:
            with patch("src.ingestion.main.upload_to_s3") as mock_upload:

                mock_extract.return_value = [
                    ("currency", '{"currency_id": 1}')
                ]

                with patch.dict(
                    "os.environ",
                    {"INGESTION_BUCKET_NAME": "test-bucket"}
                ):
                    lambda_handler(None, None)

                connection = mock_connection.return_value

                mock_extract.assert_called_once_with(connection)

                mock_upload.assert_called_once_with(
                    "currency",
                    '{"currency_id": 1}',
                    "test-bucket"
                )

                connection.close.assert_called_once()