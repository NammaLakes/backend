from fastapi import APIRouter, HTTPException
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from lakewatch.settings import settings

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
        cursor.execute(
            "SELECT * FROM node_data WHERE node_id = ?",
            (node_id,)
        )
        
        rows = cursor.fetchall()
        
        # Process the results
        result = []
        for row in rows:
            data = {
                "node_id": row["node_id"],
                # "timestamp": row["timestamp"],
                # "datetime": datetime.fromtimestamp(row["timestamp"]).isoformat(),
                "payload": json.loads(row["data"])
            }
            result.append(data)
        
        conn.close()
        
        if not result:
            return {"node_id": node_id, "message": "No data found for the last 24 hours", "data": []}
        
        return {"node_id": node_id, "count": len(result), "data": result}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")