from datetime import datetime
from unittest.mock import patch

from src.ingestion.main import lambda_handler


def test_lambda_handler():
    current_run = datetime(2026, 8, 19, 12, 10)

    with patch(
        "src.ingestion.main.get_totesys_connection"
    ) as mock_connection:
        with patch(
            "src.ingestion.main.extract_all_tables"
        ) as mock_extract:
            with patch(
                "src.ingestion.main.upload_to_s3"
            ) as mock_upload:
                with patch(
                    "src.ingestion.main.get_last_run"
                ) as mock_get_last_run:
                    with patch(
                        "src.ingestion.main.save_last_run"
                    ) as mock_save_last_run:
                        with patch(
                            "src.ingestion.main.datetime"
                        ) as mock_datetime:

                            mock_get_last_run.return_value = None
                            mock_datetime.now.return_value = current_run

                            mock_extract.return_value = [
                                (
                                    "currency",
                                    '{"currency_id": 1}',
                                )
                            ]

                            with patch.dict(
                                "os.environ",
                                {
                                    "INGESTION_BUCKET_NAME":
                                    "test-bucket"
                                },
                            ):
                                lambda_handler(None, None)

                            connection = (
                                mock_connection.return_value
                            )

                            mock_extract.assert_called_once_with(
                                connection,
                                None,
                                current_run,
                            )

                            mock_upload.assert_called_once_with(
                                "currency",
                                '{"currency_id": 1}',
                                "test-bucket",
                            )

                            connection.close.assert_called_once()

                            mock_save_last_run.assert_called_once_with(
                                "test-bucket",
                                current_run,
                            )
