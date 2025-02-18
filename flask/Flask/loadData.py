import socketio
import pandas as pd

# Initialize the Socket.IO client
sio = socketio.Client()

async def send_to_processed_pipeline(data):
    print(f"Processed Data: {data}")
    
    # Save to CSV file (or append to existing file)
    processed_df = pd.DataFrame([data])
    processed_df.to_csv('processed_data.csv', mode='a', header=False, index=False)

    # Emit via Socket.IO (if needed)
    await sio.emit('processed_data', data)
