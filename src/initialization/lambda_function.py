import logging

from .seed import seed


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting warehouse schema initialization")

    seed()

    logger.info("Warehouse schema initialization successful")

    return {
        "status": "success"
    }
