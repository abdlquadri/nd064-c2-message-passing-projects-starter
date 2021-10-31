import logging
from datetime import datetime, timedelta
from typing import Dict, List

import time
from concurrent import futures

import models
import schemas
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

import grpc
import location_pb2
import location_pb2_grpc
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-location-api")

class LocationService:

    def Get(self, request, context):
        location, coord_text = (
            db.session.query(models.Location, models.Location.coordinate.ST_AsText())
            .filter(models.Location.id == request.location_id)
            .one()
        )
        location.wkt_shape = coord_text
        return location

    def Create(self, request, context):
        print("Received a location message!")

        new_location = {
            "id": request.id,
            "person_id": request.person_id,
            "coordinate": ST_Point(request.longitude, request.latitude),
            "creation_time": request.creation_time
        }
        db.session.add(new_location)
        db.session.commit()

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
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)