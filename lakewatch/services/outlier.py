from typing import Dict, Any, List, Tuple
import numpy as np
from loguru import logger

from lakewatch.settings import settings
from lakewatch.web.api.monitoring.views import send_threshold_alert
from lakewatch.services.rabbitmq import get_rabbitmq_connection
import aio_pika
import json


class OutlierDetector:
    def __init__(self, z_threshold: float = 3.0, window_size: int = 100):
        """
        Initialize the outlier detector with a Z-score threshold and window size.
        
        Args:
            z_threshold: Number of standard deviations from the mean to consider as outlier
            window_size: Number of recent readings to consider for calculating statistics
        """
        self.z_threshold = z_threshold
        self.window_size = window_size
        self.history: Dict[str, Dict[str, List[float]]] = {}

    def update_history(self, node_id: str, data: Dict[str, float]) -> None:
        """Update the historical data for a node."""
        if node_id not in self.history:
            self.history[node_id] = {
                "temperature": [],
                "ph": [],
                "dissolved_oxygen": []
            }
        
        for key in ["temperature", "ph", "dissolved_oxygen"]:
            if key in data:
                self.history[node_id][key].append(data[key])
                if len(self.history[node_id][key]) > self.window_size:
                    self.history[node_id][key].pop(0)

    def calculate_z_score(self, value: float, values: List[float]) -> float:
        """Calculate the Z-score for a value given a list of historical values."""
        if len(values) < 2:
            return 0.0
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return 0.0
        return abs((value - mean) / std)

    def detect_outliers(self, node_id: str, data: Dict[str, float]) -> List[Tuple[str, float, float]]:
        """Detect outliers in the current data point."""
        outliers = []
        for key in ["temperature", "ph", "dissolved_oxygen"]:
            if key in data and node_id in self.history:
                z_score = self.calculate_z_score(data[key], self.history[node_id][key])
                if z_score > self.z_threshold:
                    outliers.append((key, data[key], z_score))
        return outliers


async def process_outliers(payload: Dict[str, Any]) -> None:
    """
    Process sensor data for outlier detection and send alerts if outliers are found.
    
    Args:
        payload: Dictionary containing sensor data with node information and readings
    """
    detector = OutlierDetector(z_threshold=settings.z_score_threshold)
    
    # Extract sensor data
    node_id = payload.get("node_id")
    sensor_data = {
        "temperature": payload.get("temperature"),
        "ph": payload.get("ph"),
        "dissolved_oxygen": payload.get("dissolved_oxygen")
    }
    
    # Update history and detect outliers
    detector.update_history(node_id, sensor_data)
    outliers = detector.detect_outliers(node_id, sensor_data)
    
    # Send alerts for each outlier
    for param, value, z_score in outliers:
        message = (
            f"Outlier detected for {param} at node {node_id}: "
            f"value={value:.2f}, z-score={z_score:.2f}"
        )
        await send_threshold_alert(message=message)
        logger.warning(message)
        
        # Send outlier data to dashboard via RabbitMQ
        outlier_payload = {
            "type": "outlier",
            "node_id": node_id,
            "parameter": param,
            "value": value,
            "z_score": z_score,
            "timestamp": payload.get("timestamp"),
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude")
        }
        
        try:
            connection = await get_rabbitmq_connection()
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(outlier_payload).encode(),
                    content_type="application/json"
                ),
                routing_key="dashboard"
            )
            logger.info(f"Sent outlier alert to dashboard for {param} at node {node_id}")
        except Exception as e:
            logger.error(f"Failed to send outlier alert to dashboard: {e}") 