import sqlite3
import json
from lakewatch.settings import settings

conn = sqlite3.connect(settings.db_file)
cursor = conn.cursor()

cursor.execute("SELECT node_id, timestamp, data FROM node_data")
rows = cursor.fetchall()
conn.close()

result = []
for row in rows:
    node_id, timestamp, data_json = row
    data = json.loads(data_json)  # Convert JSON string to dict
    result.append({"node_id": node_id, "timestamp": timestamp, **data})

print(result)
