# kafka_consumer.py

from kafka import KafkaConsumer
import json
import pymongo
from config import KAFKA_CONFIG, MONGO_CONFIG

mongo_client = pymongo.MongoClient(MONGO_CONFIG["host"], MONGO_CONFIG["port"])
mongo_db = mongo_client[MONGO_CONFIG["database"]]
logs_collection = mongo_db.logs

consumer = KafkaConsumer(
    KAFKA_CONFIG["topic"],
    bootstrap_servers=KAFKA_CONFIG["bootstrap_servers"],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("✅ Listening for logs...")
for message in consumer:
    logs_collection.insert_one(message.value)
    print(f"Inserted: {message.value}")
