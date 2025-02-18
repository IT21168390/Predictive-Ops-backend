import socketio

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

def emit_data(event, data):
    """Emit data to all connected clients."""
    sio.emit(event, data)

@sio.event
async def fetch_historical_data(sid, data):
    sensor = data.get("sensor")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    records = fetch_historical_data(sensor, start_date, end_date)
    await sio.emit("historical_data_response", records, to=sid)
