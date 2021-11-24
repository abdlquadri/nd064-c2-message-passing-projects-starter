import logging

from kafka import KafkaConsumer

import time

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

TOPIC_NAME = 'location'
KAFKA_SERVER = 'localhost:9092'

consumer = KafkaConsumer(TOPIC_NAME)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-location-api")


if __name__ == "__main__":
   
    # Start the Kafka consumer
    while True:
        for location in consumer:
            db.session.add(location)
            db.session.commit()
        time.sleep(86400)  
