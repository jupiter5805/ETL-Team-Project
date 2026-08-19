import logging

from src.initialization.seed import seed

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting warehouse schema seed")
    seed()
    logger.info("Warehouse schema seed success")

    return {"status": "success"}