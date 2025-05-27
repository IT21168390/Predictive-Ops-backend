import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from flask import Flask, make_response, request
from flask_cors import CORS
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub import EventData
from dotenv import load_dotenv
import socketio
import uvicorn
from concurrent.futures import ThreadPoolExecutor
import threading
import sys
import os
from diagnostics.app.extensions import mongo
from pymongo.errors import ConnectionFailure
from diagnostics.middleware.cors import add_cors_middleware

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Create FastAPI app for real-time processing
fast_app = FastAPI()

# Configure CORS for FastAPI
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Flask app for analytics and model serving
flask_app = Flask(__name__)

# Add CORS middleware for Flask
add_cors_middleware(flask_app)

# Socket.IO setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio, fast_app)

# Global variables
latest_data = {}

# Import Flask routes
from diagnostics.app.routes.analytics import analytics_bp
from diagnostics.app.routes.correlations import correlations_bp
from diagnostics.app.routes.diagnostics import diagnostics_bp
from diagnostics.app.routes.failure_analysis import failure_analysis_bp
from diagnostics.app.routes.feature_importance import feature_importance_bp
from diagnostics.app.routes.model_matrix import model_matrix_bp
from diagnostics.app.routes.instructions import instructions_bp

# Register Flask blueprints
flask_app.register_blueprint(analytics_bp, url_prefix='/analytics')
flask_app.register_blueprint(correlations_bp, url_prefix='/correlations')
flask_app.register_blueprint(diagnostics_bp, url_prefix='/diagnostics')
flask_app.register_blueprint(failure_analysis_bp, url_prefix='/failure-analysis')
flask_app.register_blueprint(feature_importance_bp, url_prefix='/model')
flask_app.register_blueprint(model_matrix_bp, url_prefix='/metrics')
flask_app.register_blueprint(instructions_bp, url_prefix='/instructions')

# Configure MongoDB
flask_app.config["MONGO_URI"] = "mongodb+srv://sarangagunasekara20:saranga20@cluster0.tnwfav4.mongodb.net/research_db"
mongo.init_app(flask_app)

# Import event processing functions
from preprocessor.services.event_processing import process_event, convert_to_sri_lankan_time
from preprocessor.services.streaming import send_to_raw_pipeline, send_to_processed_pipeline
from preprocessor.config import EVENT_HUB_CONNECTION_STRING, EVENT_HUB_NAME, CONSUMER_GROUP

async def on_event(partition_context, event: EventData):
    global latest_data
    try:
        event_body = event.body_as_json()
        print(f"Data: {event.body_as_json()}")

        # Convert timestamp
        azure_timestamp = event_body.get("timestamp")
        sri_lankan_time = convert_to_sri_lankan_time(azure_timestamp) if azure_timestamp else None
        
        # Extract raw data
        raw_data = {
            "timestamp": sri_lankan_time.isoformat(),
            "vibration_1": event_body.get("vibration_1"),
            "vibration_2": event_body.get("vibration_2"),
            "vibration_3": event_body.get("vibration_3"),
            "temperature": event_body.get("temperature"),
            "rpm": event_body.get("rpm_1"),
            "vibration_1_null_flag": event_body.get("vibration_1_null_flag"),
            "vibration_2_null_flag": event_body.get("vibration_2_null_flag"),
            "vibration_3_null_flag": event_body.get("vibration_3_null_flag"),
            "temperature_null_flag": event_body.get("temperature_null_flag"),
            "rpm_1_null_flag": event_body.get("rpm_1_null_flag"),
            "vibration_anomaly_flag": event_body.get("vibration_anomaly_flag"),
            "temperature_anomaly_flag": event_body.get("temperature_anomaly_flag"),
            "rpm_anomaly_flag": event_body.get("rpm_anomaly_flag"),
            "overall_health_status": event_body.get("overall_health_status")
        }

        processed_data = await process_event(event_body)
        
        latest_data = {
            "vibration_1": event_body.get("vibration_1"),
            "vibration_2": event_body.get("vibration_2"),
            "vibration_3": event_body.get("vibration_3"),
            "temperature": event_body.get("temperature"),
            "rpm_1": event_body.get("rpm_1"),
        }

        await send_to_raw_pipeline(raw_data)
        await send_to_processed_pipeline(processed_data)
        
    except Exception as e:
        print(f"Error processing event: {str(e)}")

async def start_eventhub_client():
    """Run the EventHub consumer client."""
    client = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STRING,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENT_HUB_NAME
    )
    async with client:
        print("Listening for events...")
        await client.receive(on_event=on_event, starting_position="@latest")

async def emit_data_to_frontend():
    while True:
        if latest_data:
            print(f"Sending data to frontend: {latest_data}")
            await sio.emit("predict_data", latest_data)
        await asyncio.sleep(60)

async def send_to_raw_pipeline(data):
    """Function to send raw data in real time"""
    print(f"Raw Data: {data}")
    await sio.emit('raw_data', data)

async def send_to_processed_pipeline(data):
    """Function to send processed data in real time"""
    print(f"Processed Data: {data}")
    await sio.emit('processed_data', data)

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

def run_flask():
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

async def run_fastapi():
    config = uvicorn.Config(sio_app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Create a thread pool executor
    executor = ThreadPoolExecutor(max_workers=1)
    
    # Start Flask in a separate thread
    executor.submit(run_flask)
    
    # Create tasks for FastAPI and event processing
    tasks = [
        run_fastapi(),
        start_eventhub_client(),
        emit_data_to_frontend()
    ]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Test MongoDB connection before running the app
try:
    # The ping command is cheap and does not require auth
    mongo.db.command('ping')
    print("MongoDB connection successful!")
except ConnectionFailure as e:
    print(f"Could not connect to MongoDB. Is it running? Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
