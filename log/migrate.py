import pymysql
import pymongo
from config import MYSQL_CONFIG, MONGO_CONFIG

# Connect to MySQL
try:
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
    print("[INFO] ✅ Connected to MySQL successfully.")
except Exception as e:
    print(f"[ERROR] ❌ MySQL connection failed: {e}")
    exit()

# Connect to MongoDB
try:
    mongo_client = pymongo.MongoClient(MONGO_CONFIG["host"], MONGO_CONFIG["port"])
    mongo_db = mongo_client[MONGO_CONFIG["database"]]
    mongo_collection = mongo_db.logs
    print("[INFO] ✅ Connected to MongoDB successfully.")
except Exception as e:
    print(f"[ERROR] ❌ MongoDB connection failed: {e}")
    mysql_conn.close()
    exit()

# Fetch logs from MySQL
try:
    mysql_cursor.execute("SELECT * FROM logs")
    logs = mysql_cursor.fetchall()
    print(f"[INFO] 📊 Retrieved {len(logs)} logs from MySQL.")
except Exception as e:
    print(f"[ERROR] ❌ Failed to fetch logs: {e}")
    mysql_conn.close()
    mongo_client.close()
    exit()

# Migrate logs to MongoDB (Avoiding Duplicates)
migrated_count = 0
for log in logs:
    # Check if the log with the same 'id' already exists
    if not mongo_collection.find_one({"id": log["id"]}):
        try:
            mongo_collection.insert_one(log)
            migrated_count += 1
        except Exception as e:
            print(f"[ERROR] ❌ Failed to migrate log {log['id']}: {e}")

print(f"✅ Successfully migrated {migrated_count} new logs to MongoDB.")

# Close connections
mysql_conn.close()
mongo_client.close()
print("[INFO] 🔒 Connections closed successfully.")
