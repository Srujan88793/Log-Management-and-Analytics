# kafka_producer.py

from kafka import KafkaProducer
import json
from config import KAFKA_CONFIG

producer = KafkaProducer(
    bootstrap_servers=KAFKA_CONFIG["bootstrap_servers"],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

log_data = {
    "log_type": "ERROR",
    "message": "Application crashed!",
    "timestamp": "2025-02-19T12:00:00"
}

producer.send(KAFKA_CONFIG["topic"], log_data)
print("✅ Log sent to Kafka")
