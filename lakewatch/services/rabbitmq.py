from typing import AsyncGenerator
import aio_pika
from aio_pika import Connection, Channel, Queue
from aio_pika.abc import AbstractIncomingMessage, AbstractConnection
import sqlite3
import json
from loguru import logger

from lakewatch.services.threshold import threshold_check
from lakewatch.services.outlier import process_outliers
from lakewatch.settings import settings


async def get_rabbitmq_connection() -> AsyncGenerator[AbstractConnection, None]:
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

            # Create data table if not exists
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS node_data (
                    node_id TEXT,
                    timestamp INTEGER,
                    temperature REAL,
                    ph REAL,
                    dissolved_oxygen REAL, 
                    PRIMARY KEY (node_id, timestamp)
                )
            """
            )

            # Create node metadata table if not exists
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS node_metadata (
                    node_id TEXT PRIMARY KEY,
                    latitude REAL,
                    longitude REAL,
                    last_updated INTEGER,
                    maintenance_required INTEGER,
                    temperature REAL,
                    dissolved_oxygen REAL,
                    ph REAL,
                    FOREIGN KEY (node_id) REFERENCES node_data (node_id)
                )
            """
            )

            # Insert data
            cursor.execute(
                "INSERT INTO node_data (node_id, timestamp, temperature, ph, dissolved_oxygen) VALUES (?, ?, ?, ?, ?)",
                (
                    data["node_id"],
                    data["timestamp"],
                    data["temperature"],
                    data["ph"],
                    data["dissolved_oxygen"],
                ),
            )

            # Insert or update node metadata
            cursor.execute(
                """
                INSERT INTO node_metadata (node_id, latitude, longitude, last_updated, maintenance_required, temperature, ph, dissolved_oxygen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                last_updated = excluded.last_updated,
                maintenance_required = excluded.maintenance_required,
                temperature = excluded.temperature,
                ph = excluded.ph,
                dissolved_oxygen = excluded.dissolved_oxygen
                WHERE node_metadata.last_updated < excluded.last_updated
                OR node_metadata.maintenance_required != excluded.maintenance_required
                """,
                (
                    data["node_id"],
                    data["latitude"],
                    data["longitude"],
                    data["timestamp"],
                    data["maintenance_required"],
                    data["temperature"],
                    data["ph"],
                    data["dissolved_oxygen"],
                ),
            )

            cursor.close()
            conn.commit()
            conn.close()

            logger.info(f"Processed message from node {data['node_id']}")
            
            # Process threshold checks and outlier detection
            await threshold_check(data)
            await process_outliers(data)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
