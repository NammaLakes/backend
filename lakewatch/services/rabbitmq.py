from typing import AsyncGenerator
import aio_pika
from aio_pika import Connection, Channel, Queue
from aio_pika.abc import AbstractIncomingMessage
import sqlite3
import json
from loguru import logger

from lakewatch.services.threshold import threshold_check
from lakewatch.settings import settings


async def get_rabbitmq_connection() -> AsyncGenerator[Connection, None]:
    """Create and yield RabbitMQ connection."""
    connection = await aio_pika.connect_robust(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
    )
    try:
        yield connection
    finally:
        await connection.close()


async def process_message(message: AbstractIncomingMessage) -> None:
    """Process incoming RabbitMQ message and save to SQLite."""
    async with message.process():
        try:
            # Parse message
            data = json.loads(message.body.decode())

            # Connect to SQLite
            conn = sqlite3.connect(settings.db_file)
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS node_data (
                    node_id TEXT,
                    timestamp INTEGER,
                    data TEXT,
                    PRIMARY KEY (node_id, timestamp)
                )
            """
            )

            # Insert data
            cursor.execute(
                "INSERT INTO node_data (node_id, timestamp, data) VALUES (?, ?, ?)",
                (data["node_id"], data["timestamp"], json.dumps(data["payload"])),
            )

            conn.commit()
            conn.close()

            logger.info(f"Processed message from node {data['node_id']}")

            # Check thresholds
            await threshold_check(data["payload"])

        except Exception as e:
            logger.error(f"Error processing message: {e}")
