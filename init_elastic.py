import os
import urllib3
from elasticsearch import Elasticsearch

# Suppress self-signed certificate warnings for local development logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Your exact secure local parameters from your terminal setup
ES_HOST = "https://localhost:9200"
ES_USER = "elastic"
ES_PASSWORD = "qUKn3=DHhkyrcYtr=sxj"

# Initialize the secure local client instance
es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False  # Required because the local auto-generated SSL cert is self-signed
)

def initialize_indices():
    # 1. Define worldcup-incidents Mapping
    if not es.indices.exists(index="worldcup-incidents"):
        es.indices.create(
            index="worldcup-incidents",
            mappings={
                "properties": {
                    "incident_id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "severity": {"type": "keyword"},
                    "zone_affected": {"type": "keyword"},
                    "description": {"type": "text"},
                    "status": {"type": "keyword"}
                }
            }
        )
        print("Created index: worldcup-incidents")

    # 2. Define worldcup-schedule Mapping
    if not es.indices.exists(index="worldcup-schedule"):
        es.indices.create(
            index="worldcup-schedule",
            mappings={
                "properties": {
                    "match_id": {"type": "keyword"},
                    "teams": {"type": "text"},
                    "stadium_attendance": {"type": "integer"},
                    "match_status": {"type": "keyword"},
                    "game_minute": {"type": "integer"}
                }
            }
        )
        print("Created index: worldcup-schedule")

    # 3. Define worldcup-logistics Mapping
    if not es.indices.exists(index="worldcup-logistics"):
        es.indices.create(
            index="worldcup-logistics",
            mappings={
                "properties": {
                    "asset_id": {"type": "keyword"},
                    "asset_type": {"type": "keyword"},
                    "location": {"type": "geo_point"},
                    "passenger_capacity": {"type": "integer"},
                    "current_status": {"type": "keyword"}
                }
            }
        )
        print("Created index: worldcup-logistics")

def seed_mock_data():
    # Seed live match telemetry matching your image layout
    es.index(index="worldcup-schedule", id="match-la-01", document={
        "match_id": "match-la-01",
        "teams": "USA vs. Germany",
        "stadium_attendance": 72000,
        "match_status": "LIVE",
        "game_minute": 85
    })

    # Seed initial asset pool matching image_c3cc8b.png
    shuttles = [
        {"asset_id": "Shuttle-104", "asset_type": "shuttle_bus", "location": {"lat": 33.953, "lon": -118.339}, "passenger_capacity": 80, "current_status": "Idle"},
        {"asset_id": "Shuttle-112", "asset_type": "shuttle_bus", "location": {"lat": 33.951, "lon": -118.335}, "passenger_capacity": 80, "current_status": "Idle"},
        {"asset_id": "Shuttle-201", "asset_type": "shuttle_bus", "location": {"lat": 33.940, "lon": -118.320}, "passenger_capacity": 50, "current_status": "Active"}
    ]
    for s in shuttles:
        es.index(index="worldcup-logistics", id=s["asset_id"], document=s)
        
    print("Successfully seeded initial telemetry data to secure local Elastic cluster!")

if __name__ == "__main__":
    try:
        print("Connecting to Elastic...")
        initialize_indices()
        seed_mock_data()
    except Exception as e:
        print(f"Initialization failed: {e}")