from typing import AsyncGenerator
import aio_pika
from aio_pika import Connection
from aio_pika.abc import AbstractIncomingMessage
import aiosqlite
import json
from loguru import logger

from lakewatch.settings import settings

async def get_rabbitmq_connection() -> AsyncGenerator[Connection, None]:
    """Create and yield RabbitMQ connection."""
    connection = await aio_pika.connect_robust(
        f"amqp://{settings.rabbitmq_host}:{settings.rabbitmq_port}"
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

            # Validate required keys
            if not all(k in data for k in ("node_id", "timestamp", "payload")):
                logger.error(f"Invalid message format: {data}")
                return

            # Store in SQLite (using async `aiosqlite`)
            async with aiosqlite.connect(settings.db_file) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS node_data (
                        node_id TEXT,
                        timestamp INTEGER,
                        data TEXT,
                        PRIMARY KEY (node_id, timestamp)
                    )
                """)
                await db.execute(
                    "INSERT INTO node_data (node_id, timestamp, data) VALUES (?, ?, ?)",
                    (data["node_id"], data["timestamp"], json.dumps(data["payload"]))
                )
                await db.commit()

            logger.info(f"Processed message from node {data['node_id']}")

        except json.JSONDecodeError:
            logger.error("Failed to decode message as JSON")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
