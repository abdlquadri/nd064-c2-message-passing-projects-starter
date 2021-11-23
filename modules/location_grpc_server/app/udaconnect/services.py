import logging
from datetime import datetime, timedelta
from typing import Dict, List

from kafka import KafkaProducer, KafkaConsumer

import time
from concurrent import futures

from models import Location
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

import grpc
from location_proto import location_pb2
from location_proto import location_pb2_grpc
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

TOPIC_NAME = 'items'
KAFKA_SERVER = 'localhost:9092'


producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
consumer = KafkaConsumer(TOPIC_NAME)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-location-api")

class LocationService:

    def Get(self, request, context):
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == request.location_id)
            .one()
        )
        location.wkt_shape = coord_text
        return location
    

    def find_by_person(person_id: int, start_date: datetime, end_date: datetime, meters=5) -> List[Location]:
        locations =db.session.query(Location).filter(
            Location.person_id == person_id
        ).filter(Location.creation_time < end_date).filter(
            Location.creation_time >= start_date
        ).all()
        result = location_pb2.LocationMessageList()
        result.locations.extend(locations)
        return result


    def Create(self, request, context):
        print("Received a location message!")
        new_location = {
            "id": request.id,
            "person_id": request.person_id,
            "coordinate": ST_Point(request.longitude, request.latitude),
            "creation_time": request.creation_time
        }
        producer.send(TOPIC_NAME, new_location)
        producer.flush()
        return location_pb2.LocationMessage(**new_location)


if __name__ == "__main__":
   
    # Initialize gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    location_pb2_grpc.add_LocationServiceServicer_to_server(LocationService(), server)


    print("Server starting on port 5005...")
    server.add_insecure_port("[::]:5005")
    server.start()
    # Keep thread alive
    try:
        while True:
            for location in consumer:
                db.session.add(location)
                db.session.commit()
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)    
