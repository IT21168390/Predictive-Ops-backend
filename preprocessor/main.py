# import asyncio
# from azure.eventhub.aio import EventHubConsumerClient
# from azure.eventhub import EventData
# #from firebase_handler import store_anomaly_record
# from services.event_processing import process_event, convert_to_sri_lankan_time
# #from app.services.streaming import send_to_raw_pipeline, send_to_processed_pipeline
# from config import EVENT_HUB_CONNECTION_STRING, EVENT_HUB_NAME, CONSUMER_GROUP

# import socketio
# import uvicorn
# from fastapi import FastAPI

# # FastAPI and Socket.IO setup
# app = FastAPI()
# sio = socketio.AsyncServer(async_mode='asgi', 
#                            cors_allowed_origins="*" 
#                            )  
# sio_app = socketio.ASGIApp(sio, app)

# app.mount("/socket.io", sio_app)


# async def on_event(partition_context, event: EventData):
#     try:
#         event_body = event.body_as_json()
#         print(f"Data: {event.body_as_json()}")

#         # Convert timestamp
#         azure_timestamp = event_body.get("timestamp")
#         sri_lankan_time = convert_to_sri_lankan_time(azure_timestamp) if azure_timestamp else None
#         # Extract raw data
#         raw_data = {
#             "timestamp": sri_lankan_time.isoformat(),

#             "vibration_1": event_body.get("vibration_1"),
#             "vibration_2": event_body.get("vibration_2"),
#             "vibration_3": event_body.get("vibration_3"),
#             "temperature": event_body.get("temperature"),
#             "rpm": event_body.get("rpm_1"),

#             "vibration_1_null_flag": event_body.get("vibration_1_null_flag"),
#             "vibration_2_null_flag": event_body.get("vibration_2_null_flag"),
#             "vibration_3_null_flag": event_body.get("vibration_3_null_flag"),
#             "temperature_null_flag": event_body.get("temperature_null_flag"),
#             "rpm_1_null_flag": event_body.get("rpm_1_null_flag"),

#             "vibration_anomaly_flag": event_body.get("vibration_anomaly_flag"),
#             "temperature_anomaly_flag": event_body.get("temperature_anomaly_flag"),
#             "rpm_anomaly_flag": event_body.get("rpm_anomaly_flag"),
#             "overall_health_status": event_body.get("overall_health_status")
#         }

#         processed_data = await process_event(event_body)
        
#         await send_to_raw_pipeline(raw_data)
#         await send_to_processed_pipeline(processed_data)
#         #print(f"Processed and forwarded data: {processed_data}")
#     except Exception as e:
#         print(f"Error processing event: {str(e)}")

# async def start_eventhub_client():
#     """Run the EventHub consumer client."""
#     client = EventHubConsumerClient.from_connection_string(
#         conn_str=EVENT_HUB_CONNECTION_STRING,
#         consumer_group=CONSUMER_GROUP,
#         eventhub_name=EVENT_HUB_NAME
#     )
#     async with client:
#         print("Listening for events...")
#         await client.receive(on_event=on_event, starting_position="@latest")

# # Event for connecting clients
# @sio.event
# async def connect(sid, environ):
#     print(f"Client connected: {sid}")

# # Event for disconnecting clients
# @sio.event
# async def disconnect(sid):
#     print(f"Client disconnected: {sid}")

# # Function to send raw data in real time
# async def send_to_raw_pipeline(data):
#     print(f"Raw Data: {data}")
#     await sio.emit('raw_data', data)

# # Function to send processed data in real time
# async def send_to_processed_pipeline(data):
#     print(f"Processed Data: {data}")
#     await sio.emit('processed_data', data)

# async def run():
#     # Start the EventHub client
#     eventhub_client = asyncio.create_task(start_eventhub_client())
    
#     # Start the FastAPI server
#     config = uvicorn.Config(app, host="0.0.0.0", port=8000)
#     server = uvicorn.Server(config)
#     server_task = asyncio.create_task(server.serve())

#     # Wait for both tasks to finish
#     await asyncio.gather(eventhub_client, server_task)

# if __name__ == "__main__":
#     # Run both the FastAPI server and the EventHub client concurrently
#     asyncio.run(run())

import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub import EventData
from config import EVENT_HUB_CONNECTION_STRING, EVENT_HUB_NAME, CONSUMER_GROUP
import socketio
import uvicorn
from fastapi import FastAPI

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio, app)
app.mount("/socket.io", sio_app)

latest_data = {}

async def on_event(partition_context, event: EventData):
    global latest_data
    try:
        event_body = event.body_as_json()
        print(f"Data received: {event_body}")

        latest_data = {
            "vibration_1": event_body.get("vibration_1"),
            "vibration_2": event_body.get("vibration_2"),
            "vibration_3": event_body.get("vibration_3"),
            "temperature": event_body.get("temperature"),
            "rpm_1": event_body.get("rpm_1"),
        }
    except Exception as e:
        print(f"Error processing event: {str(e)}")

async def start_eventhub_client():
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

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

async def run():
    eventhub_task = asyncio.create_task(start_eventhub_client())
    emit_task = asyncio.create_task(emit_data_to_frontend())

    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())

    await asyncio.gather(eventhub_task, emit_task, server_task)

if __name__ == "__main__":
    asyncio.run(run())
