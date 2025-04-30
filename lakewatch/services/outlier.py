from typing import Dict, Any, List
import sqlite3
import logging as logger

from lakewatch.settings import settings
from lakewatch.web.api.monitoring.views import send_threshold_alert


async def process_outliers(payload: Dict[str, Any]) -> None:
    """
    Detect and handle outliers in sensor readings compared to recent historical data.

    Args:
        payload: Dictionary containing sensor data with node information and readings
    """
    node_id = payload.get("node_id")
    temperature = payload.get("temperature")
    ph = payload.get("ph")
    dissolved_oxygen = payload.get("dissolved_oxygen")

    try:
        conn = sqlite3.connect(settings.db_file)
        cursor = conn.cursor()

        # Fetch last 5 readings for this node
        cursor.execute(
            """
            SELECT temperature, ph, dissolved_oxygen
            FROM node_data
            WHERE node_id = ?
            ORDER BY timestamp DESC
            LIMIT 5
        """,
            (node_id,),
        )
        rows = cursor.fetchall()

        conn.close()
        if not rows or len(rows) < 3:
            return

        # Calculate simple means of recent values
        recent_temp = [r[0] for r in rows]
        recent_ph = [r[1] for r in rows]
        recent_oxygen = [r[2] for r in rows]

        def is_outlier(
            current: float, history: List[float], factor: float = 0.7
        ) -> bool:
            mean = sum(history) / len(history)
            deviation = abs(current - mean)
            return deviation > (factor * (max(history) - min(history)) / 2)

        if temperature is not None and is_outlier(float(temperature), recent_temp):
            await send_threshold_alert(
                message=f"Outlier detected in temperature: {temperature}"
            )
            logger.warning(
                f"Node {node_id}: Outlier detected in temperature: {temperature}"
            )

        if ph is not None and is_outlier(float(ph), recent_ph):
            await send_threshold_alert(message=f"Outlier detected in pH: {ph}")
            logger.warning(f"Node {node_id}: Outlier detected in pH: {ph}")

        if dissolved_oxygen is not None and is_outlier(
            float(dissolved_oxygen), recent_oxygen
        ):
            await send_threshold_alert(
                message=f"Outlier detected in dissolved oxygen: {dissolved_oxygen}"
            )
            logger.warning(
                f"Node {node_id}: Outlier detected in dissolved oxygen: {dissolved_oxygen}"
            )

    except Exception as e:
        logger.error(f"Error during outlier processing: {e}")
