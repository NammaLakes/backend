from fastapi import APIRouter, HTTPException
import sqlite3
from datetime import datetime
from typing import Dict, Any
from loguru import logger

from lakewatch.settings import settings

router = APIRouter()


@router.get("/")
def get_data() -> Dict[str, Any]:
    """
    Get node info from the database.
    :return: node info from the database.
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(settings.db_file))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM node_metadata")

        rows = cursor.fetchall()

        result = []
        for row in rows:
            try:
                data = {
                    "node_id": row["node_id"],
                    "timestamp": row["last_updated"],
                    "datetime": datetime.fromtimestamp(row["last_updated"]).isoformat(),
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "temperature": row["temperature"],
                    "ph": row["ph"],
                    "dissolved_oxygen": row["dissolved_oxygen"],
                    "maintenance_required": row["maintenance_required"],
                }
                result.append(data)
            except KeyError as e:
                logger.error(f"Error processing node data: {e} for row: {dict(row)}")
                continue
        conn.close()

        if not result:
            return {
                "message": "No nodes found",
            }

        return {"count": len(result), "data": result}

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")
