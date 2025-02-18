import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("key/predictivemaintenancesystem-firebase-adminsdk-w2tny-15b2aec14c.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

async def send_to_raw_pipeline(data):
    """Store raw data in Firestore."""
    try:
        doc_ref = db.collection("raw_data").document()
        doc_ref.set(data)
        print("Raw data stored successfully")
    except Exception as e:
        print(f"Failed to store raw data: {e}")

async def send_to_processed_pipeline(data):
    """Store processed data in Firestore."""
    try:
        doc_ref = db.collection("processed_data").document()
        doc_ref.set(data)
        print("Processed data stored successfully")
    except Exception as e:
        print(f"Failed to store processed data: {e}")


async def store_anomaly_record(timestamp, anomalies, nulls, sensorData):
    """Store anomaly records in Firestore."""
    try:
        doc_ref = db.collection("anomalies").document(str(timestamp))
        doc_ref.set({
            #"sensor": sensor,
            "timestamp": timestamp,
            #"details": details,
            "anomalies": anomalies,
            "nulls": nulls,
            "sensorData": sensorData
        })
        print("Anomaly record stored successfully.")
    except Exception as e:
        print(f"Failed to store anomaly record: {e}")


# def fetch_historical_data(sensor, start_date, end_date):
#     try:
#         records = db.collection("processed_data").where(
#             "sensor", "==", sensor
#         ).where(
#             "timestamp", ">=", start_date
#         ).where(
#             "timestamp", "<=", end_date
#         ).stream()
#         return [record.to_dict() for record in records]
#     except Exception as e:
#         print(f"Failed to fetch historical data: {e}")
def fetch_historical_anomalies(sensor=None, anomaly_type=None, start_date=None, end_date=None):
    try:
        query = db.collection("anomalies")
        if sensor:
            query = query.where("sensor", "==", sensor)
        if anomaly_type:
            query = query.where("details.type", "==", anomaly_type)
        if start_date and end_date:
            query = query.where("timestamp", ">=", start_date).where("timestamp", "<=", end_date)
        
        records = query.stream()
        return [record.to_dict() for record in records]
    except Exception as e:
        print(f"Failed to fetch anomaly records: {e}")



# def store_data(collection, document, data):
#     """Store data in Firestore."""
#     db.collection(collection).document(document).set(data)

# def add_anomaly_record(record):
#     """Add anomaly record."""
#     db.collection("anomalies").add(record)

def get_historical_data(sensor_type, start_time, end_time):
    """Query historical data for analysis."""
    return db.collection("processed_data") \
        .where("sensor_type", "==", sensor_type) \
        .where("timestamp", ">=", start_time) \
        .where("timestamp", "<=", end_time) \
        .stream()
