import asyncio
import statistics
from datetime import datetime, timedelta
from collections import deque
import pytz
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from firebase_admin import credentials, firestore, initialize_app
from socketio import AsyncServer
import socketio

# Firebase Setup
cred = credentials.Certificate("path/to/your-firebase-key.json")
initialize_app(cred)
db = firestore.client()
raw_data_collection = db.collection("raw_data")
processed_data_collection = db.collection("processed_data")
anomaly_records_collection = db.collection("anomaly_records")

# Socket.io Setup
sio = AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

# Anomaly Tracking
anomaly_counts = {}

# Helper Functions
def convert_to_sri_lankan_time(utc_timestamp):
    try:
        normalized_timestamp = utc_timestamp[:26] + 'Z'
        utc_time = datetime.strptime(normalized_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        sri_lanka_tz = pytz.timezone("Asia/Colombo")
        return utc_time.replace(tzinfo=pytz.utc).astimezone(sri_lanka_tz)
    except ValueError as ve:
        raise ValueError(f"Failed to parse timestamp '{utc_timestamp}': {ve}")

def handle_outliers(data_list, method="z_score", threshold=3):
    data_array = np.array(data_list)
    if method == "z_score":
        mean = np.mean(data_array)
        std = np.std(data_array)
        z_scores = (data_array - mean) / std
        return [
            value if abs(z) <= threshold else mean
            for value, z in zip(data_array, z_scores)
        ]
    return data_list

def compute_statistics(data_list):
    data_array = np.array(data_list)
    return {
        "mean": np.mean(data_array),
        "median": np.median(data_array),
        "std_dev": np.std(data_array),
        "min": np.min(data_array),
        "max": np.max(data_array),
    }

async def send_email(to_email, subject, body):
    sender_email = "your-email@example.com"
    sender_password = "your-password"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())

async def process_anomalies(sensor, anomaly_flag, value, timestamp):
    if anomaly_flag != "Normal":
        anomaly_counts[sensor] = anomaly_counts.get(sensor, 0) + 1
        if anomaly_counts[sensor] >= 30:  # 30 consecutive readings (e.g., 5 minute)
            alert_message = f"Persistent anomaly detected in {sensor}. Current value: {value}."
            await send_email("maintenance@example.com", f"Anomaly Alert: {sensor}", alert_message)
            anomaly_records_collection.add({
                "sensor": sensor,
                "value": value,
                "timestamp": timestamp,
                "message": alert_message
            })
    else:
        anomaly_counts[sensor] = 0

# Async function to process events
async def on_event(partition_context, event):
    event_body = event.body_as_json()
    azure_timestamp = event_body.get("timestamp")
    sri_lankan_time = convert_to_sri_lankan_time(azure_timestamp) if azure_timestamp else None
    raw_data = {key: event_body.get(key) for key in ["vibration_1", "vibration_2", "temperature", "rpm"]}
    anomaly_flags = {key: event_body.get(key) for key in ["vibration_anomaly_flag", "temperature_anomaly_flag", "rpm_anomaly_flag"]}

    # Store raw data in Firestore
    raw_data["timestamp"] = sri_lankan_time
    raw_data_collection.add(raw_data)

    # Process data
    processed_data = {key: handle_outliers([value]) for key, value in raw_data.items()}
    stats_data = {key: compute_statistics([value]) for key, value in processed_data.items()}

    # Store processed data in Firestore
    processed_data_collection.add({"timestamp": sri_lankan_time, "data": processed_data, "statistics": stats_data})

    # Emit data to frontend
    await sio.emit("data_update", {"raw_data": raw_data, "processed_data": processed_data, "statistics": stats_data})

    # Handle anomalies
    for sensor, flag in anomaly_flags.items():
        await process_anomalies(sensor, flag, raw_data.get(sensor), sri_lankan_time)

async def main():
    # EventHubConsumerClient setup goes here
    pass

if __name__ == "__main__":
    asyncio.run(main())
