from loguru import logger

from lakewatch.settings import settings
from lakewatch.web.api.monitoring.views import send_threshold_alert


async def threshold_check(payload):
    for key, value in payload.items():
        if key == "temperature":
            if value > settings.temperature_threshold:
                await send_threshold_alert(
                    message="Temperature threshold exceeded: {value}"
                )
                logger.info(f"Temperature threshold exceeded: {value}")
        elif key == "humidity":
            if value > settings.humidity_threshold:
                await send_threshold_alert(
                    message="Humidity threshold exceeded: {value}"
                )
                logger.info(f"Humidity threshold exceeded: {value}")
        elif key == "ph":
            await send_threshold_alert(message="pH threshold exceeded: {value}")
            if value > settings.ph_threshold:
                logger.info(f"pH threshold exceeded: {value}")
        elif key == "turbidity":
            await send_threshold_alert(message="Turbidity threshold exceeded: {value}")
            if value > settings.turbidity_threshold:
                logger.info(f"Turbidity threshold exceeded: {value}")
        elif key == "conductivity":
            await send_threshold_alert(
                message="Conductivity threshold exceeded: {value}"
            )
            if value > settings.conductivity_threshold:
                logger.info(f"Conductivity threshold exceeded: {value}")
        elif key == "oxygen":
            await send_threshold_alert(message="Oxygen threshold exceeded: {value}")
            if value > settings.oxygen_threshold:
                logger.info(f"Oxygen threshold exceeded: {value}")
        else:
            logger.error(f"Unknown key: {key}")
