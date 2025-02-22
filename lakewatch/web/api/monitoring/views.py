from fastapi import APIRouter, HTTPException
import sqlite3
import json
from datetime import datetime, timedelta
from lakewatch.settings import settings

router = APIRouter()

@router.get("/nodes/{node_id}")
async def get_node_data(node_id: int):
    """
    Fetch the last 3 hours of data for a given node_id from SQLite.
    """
    conn = sqlite3.connect(settings.db_file)
    cursor = conn.cursor()

    # Calculate timestamp for 3 hours ago
    three_hours_ago = datetime.utcnow() - timedelta(hours=3)
    timestamp_threshold = three_hours_ago.strftime("%Y-%m-%d %H:%M:%S")

    # Query the database
    cursor.execute(
        """
        SELECT node_id, timestamp, data 
        FROM node_data 
        WHERE node_id = ? AND timestamp >= ?
        ORDER BY timestamp DESC
        """,
        (node_id, timestamp_threshold),
    )

    rows = cursor.fetchall()
    conn.close()

    # If no data found, return a 404 response
    if not rows:
        raise HTTPException(status_code=404, detail="No data found in the last 3 hours")

    # Process the results
    result = []
    for row in rows:
        node_id, timestamp, data_json = row
        data = json.loads(data_json)  # Convert JSON string to dictionary
        result.append({"node_id": node_id, "timestamp": timestamp, **data})

    return {"node_id": node_id, "last_3_hours_data": result}
