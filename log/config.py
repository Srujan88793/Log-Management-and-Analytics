# config.py

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "your_mysql_user",
    "password": "your_mysql_password",
    "database": "your_mysql_db",
}


MONGO_CONFIG = {
    "host": "localhost",
    "port": 27017,
    "database": "logs_db",
}

KAFKA_CONFIG = {
    "bootstrap_servers": "localhost:9092",
    "topic": "log_topic",
}
