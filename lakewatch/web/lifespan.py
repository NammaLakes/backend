from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
import aio_pika
from loguru import logger

from lakewatch.settings import settings
from lakewatch.services.rabbitmq import process_message


@asynccontextmanager
async def lifespan_setup(app: FastAPI) -> AsyncGenerator[None, None]:
    """Setup lifespan events."""
    # Connect to RabbitMQ
    connection = await aio_pika.connect_robust(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
    )

    # Create channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=100)

    # Declare queue
    queue = await channel.declare_queue(settings.rabbitmq_queue, durable=True)

    # Start consuming messages
    await queue.consume(process_message)
    logger.info("RabbitMQ consumer started")

    app.state.rabbitmq_connection = connection

    yield

    # Cleanup
    await connection.close()
    logger.info("RabbitMQ connection closed")
