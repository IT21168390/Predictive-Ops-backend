# async def send_to_raw_pipeline(data):
#     """Stream raw data to a specified endpoint."""
#     print(f"Raw Data: {data}")
#     # Implement actual streaming logic here.

# async def send_to_processed_pipeline(data):
#     """Stream processed data to a specified endpoint."""
#     print(f"Processed Data: {data}")
#     # Implement actual streaming logic here.



import socketio
import uvicorn
from fastapi import FastAPI

# Create a Socket.IO server instance
sio = socketio.AsyncServer()
app = FastAPI()

# Attach the Socket.IO server to the FastAPI app
app.mount("/socket.io", socketio.ASGIApp(sio))

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

# Run the app with uvicorn to specify the port
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# import socketio
# import asyncio

# # Create a Socket.IO server instance
# sio = socketio.AsyncServer(async_mode='asgi')
# app = socketio.ASGIApp(sio)

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

# Example task to send data periodically
# async def periodic_data_sender():
#     while True:
#         raw_data = {"sensor": "vibration", "value": 5.5}
#         processed_data = {"sensor": "vibration", "status": "Anomaly"}
#         await send_to_raw_pipeline(raw_data)
#         await send_to_processed_pipeline(processed_data)
#         await asyncio.sleep(1)  # Simulate periodic data
