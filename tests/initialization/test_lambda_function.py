from unittest.mock import patch

from src.initialization import lambda_function


@patch.object(
    lambda_function,
    "seed",
)
def test_lambda_handler_calls_seed(
    mock_seed,
):
    result = lambda_function.lambda_handler(
        {},
        None,
    )

    mock_seed.assert_called_once()

    assert result == {
        "status": "success"
    }