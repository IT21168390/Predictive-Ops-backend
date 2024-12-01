# import asyncio
# import statistics
# from datetime import datetime, timedelta
# from collections import deque
# import pytz
# import numpy as np
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from typing import List
# from firebase_admin import credentials, firestore, initialize_app
# from socketio import AsyncServer
# import socketio

# # Firebase Setup
# cred = credentials.Certificate("path/to/your-firebase-key.json")
# initialize_app(cred)
# db = firestore.client()
# raw_data_collection = db.collection("raw_data")
# processed_data_collection = db.collection("processed_data")
# anomaly_records_collection = db.collection("anomaly_records")

# # Socket.io Setup
# sio = AsyncServer(async_mode='asgi')
# app = socketio.ASGIApp(sio)

# # Anomaly Tracking
# anomaly_counts = {}

# # Helper Functions
# def convert_to_sri_lankan_time(utc_timestamp):
#     try:
#         normalized_timestamp = utc_timestamp[:26] + 'Z'
#         utc_time = datetime.strptime(normalized_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
#         sri_lanka_tz = pytz.timezone("Asia/Colombo")
#         return utc_time.replace(tzinfo=pytz.utc).astimezone(sri_lanka_tz)
#     except ValueError as ve:
#         raise ValueError(f"Failed to parse timestamp '{utc_timestamp}': {ve}")

# def handle_outliers(data_list, method="z_score", threshold=3):
#     data_array = np.array(data_list)
#     if method == "z_score":
#         mean = np.mean(data_array)
#         std = np.std(data_array)
#         z_scores = (data_array - mean) / std
#         return [
#             value if abs(z) <= threshold else mean
#             for value, z in zip(data_array, z_scores)
#         ]
#     return data_list

# def compute_statistics(data_list):
#     data_array = np.array(data_list)
#     return {
#         "mean": np.mean(data_array),
#         "median": np.median(data_array),
#         "std_dev": np.std(data_array),
#         "min": np.min(data_array),
#         "max": np.max(data_array),
#     }

# async def send_email(to_email, subject, body):
#     sender_email = "your-email@example.com"
#     sender_password = "your-password"
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     with smtplib.SMTP("smtp.example.com", 587) as server:
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.sendmail(sender_email, to_email, msg.as_string())

# async def process_anomalies(sensor, anomaly_flag, value, timestamp):
#     if anomaly_flag != "Normal":
#         anomaly_counts[sensor] = anomaly_counts.get(sensor, 0) + 1
#         if anomaly_counts[sensor] >= 30:  # 30 consecutive readings (e.g., 5 minute)
#             alert_message = f"Persistent anomaly detected in {sensor}. Current value: {value}."
#             await send_email("maintenance@example.com", f"Anomaly Alert: {sensor}", alert_message)
#             anomaly_records_collection.add({
#                 "sensor": sensor,
#                 "value": value,
#                 "timestamp": timestamp,
#                 "message": alert_message
#             })
#     else:
#         anomaly_counts[sensor] = 0

# # Async function to process events
# async def on_event(partition_context, event):
#     event_body = event.body_as_json()
#     azure_timestamp = event_body.get("timestamp")
#     sri_lankan_time = convert_to_sri_lankan_time(azure_timestamp) if azure_timestamp else None
#     raw_data = {key: event_body.get(key) for key in ["vibration_1", "vibration_2", "temperature", "rpm"]}
#     anomaly_flags = {key: event_body.get(key) for key in ["vibration_anomaly_flag", "temperature_anomaly_flag", "rpm_anomaly_flag"]}

#     # Store raw data in Firestore
#     raw_data["timestamp"] = sri_lankan_time
#     raw_data_collection.add(raw_data)

#     # Process data
#     processed_data = {key: handle_outliers([value]) for key, value in raw_data.items()}
#     stats_data = {key: compute_statistics([value]) for key, value in processed_data.items()}

#     # Store processed data in Firestore
#     processed_data_collection.add({"timestamp": sri_lankan_time, "data": processed_data, "statistics": stats_data})

#     # Emit data to frontend
#     await sio.emit("data_update", {"raw_data": raw_data, "processed_data": processed_data, "statistics": stats_data})

#     # Handle anomalies
#     for sensor, flag in anomaly_flags.items():
#         await process_anomalies(sensor, flag, raw_data.get(sensor), sri_lankan_time)

# async def main():
#     # EventHubConsumerClient setup goes here
#     pass

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub import EventData
#from firebase_handler import store_anomaly_record
from services.event_processing import process_event, convert_to_sri_lankan_time
#from app.services.streaming import send_to_raw_pipeline, send_to_processed_pipeline
from config import EVENT_HUB_CONNECTION_STRING, EVENT_HUB_NAME, CONSUMER_GROUP

import socketio
import uvicorn
from fastapi import FastAPI




async def on_event(partition_context, event: EventData):
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
        
        await send_to_raw_pipeline(raw_data)
        await send_to_processed_pipeline(processed_data)
        #print(f"Processed and forwarded data: {processed_data}")
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

# Event for connecting clients
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

# Event for disconnecting clients
@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Function to send raw data in real time
async def send_to_raw_pipeline(data):
    print(f"Raw Data: {data}")
    await sio.emit('raw_data', data)

# Function to send processed data in real time
async def send_to_processed_pipeline(data):
    print(f"Processed Data: {data}")
    await sio.emit('processed_data', data)

async def run():
    # Start the EventHub client
    eventhub_client = asyncio.create_task(start_eventhub_client())
    
    # Start the FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())

    # Wait for both tasks to finish
    await asyncio.gather(eventhub_client, server_task)

if __name__ == "__main__":
    # Run both the FastAPI server and the EventHub client concurrently
    asyncio.run(run())