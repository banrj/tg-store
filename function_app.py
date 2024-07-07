from app.core.log_config import logger
from datetime import datetime

from app.main import create_app as create_fastapi_app
from app.yc.dispatcher import Dispatcher


async def handle(event, context):
    logger.info(f"APPLICATION STARTUP {datetime.now()}")
    logger.debug(f'{event=}')

    fastapi_app = create_fastapi_app()
    logger.info(f"FASTAPi {datetime.now()}")

    dispatcher = Dispatcher(fastapi_app)
    logger.info(f"DISPATCHER YC {datetime.now()}")

    try:
        response = await dispatcher.start_event(event, context)
    except Exception as e:
        logger.error(f"Error during handling: {e}")
        return {
            "statusCode": 500,
            "body": "Internal Server Error",
        }

    return response
