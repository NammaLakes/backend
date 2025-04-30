from fastapi import APIRouter, HTTPException, Query
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from lakewatch.settings import settings
from .analysis import detect_outliers

router = APIRouter()


@router.get("/{node_id}")
def get_data(node_id: str) -> Dict[str, Any]:
    """
    Get data from the node for the last 24 hours.

    :param node_id: node identifier.
    :return: data from the node for the last 24 hours.
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(settings.db_file))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Execute query to get data for the specified node_id in the last 24 hours
        cursor.execute("SELECT * FROM node_data WHERE node_id = ?", (node_id,))

        rows = cursor.fetchall()

        # Process the results
        result = []
        for row in rows:
            data = {
                "node_id": row["node_id"],
                # "timestamp": row["timestamp"],
                # "datetime": datetime.fromtimestamp(row["timestamp"]).isoformat(),
                "payload": json.loads(row["data"]),
            }
            result.append(data)

        conn.close()

        if not result:
            return {
                "node_id": node_id,
                "message": "No data found for the last 24 hours",
                "data": [],
            }

        return {"node_id": node_id, "count": len(result), "data": result}

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

@router.get("/{node_id}/outliers")
def get_outliers(
    node_id: str,
    value_key: str = Query(..., description="Key in the payload to analyze for outliers"),
    z_threshold: float = Query(2.0, description="Z-score threshold for outlier detection")
) -> Dict[str, Any]:
    """
    Get data from the node and detect outliers based on Z-score analysis.

    :param node_id: node identifier
    :param value_key: key in the payload to analyze
    :param z_threshold: Z-score threshold for outlier detection
    :return: normal and outlier data points
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(settings.db_file))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Execute query to get data for the specified node_id
        cursor.execute("SELECT * FROM node_data WHERE node_id = ?", (node_id,))

        rows = cursor.fetchall()

        # Process the results
        data = []
        for row in rows:
            point = {
                "node_id": row["node_id"],
                "payload": json.loads(row["data"]),
            }
            data.append(point)

        conn.close()

        if not data:
            return {
                "node_id": node_id,
                "message": "No data found",
                "normal_points": [],
                "outlier_points": [],
            }

        # Detect outliers
        normal_points, outlier_points = detect_outliers(data, value_key, z_threshold)

        return {
            "node_id": node_id,
            "total_points": len(data),
            "normal_points_count": len(normal_points),
            "outlier_points_count": len(outlier_points),
            "normal_points": normal_points,
            "outlier_points": outlier_points,
        }

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid value_key: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
