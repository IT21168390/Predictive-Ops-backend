from collections import deque, defaultdict
from datetime import datetime
import pytz
from collections import Counter
from helpers.anomaly import handle_anomalies, handle_outliers, validate_and_correct
from helpers.statistics import compute_statistics
#from email_handler import send_anomaly_email, send_detailed_anomaly_email
from firebase_handler import store_anomaly_record





# Rolling buffer to store sensor data for 5 minutes (300 seconds / 10-second intervals = 30 slots)
rolling_buffer = defaultdict(lambda: deque(maxlen=30))

def generate_anomaly_report(rolling_buffer):
    """Generate a detailed anomaly report from the rolling buffer."""
    report = "Anomaly Report (Last 5 Minutes):\n\n"
    for sensor, readings in rolling_buffer.items():
        report += f"Sensor: {sensor}\n"
        for timestamp, value, null_flag, anomaly_flag in readings:
            report += (
                f"Timestamp: {timestamp}, Value: {value}, Null Flag: {null_flag}, "
                f"Anomaly Flag: {anomaly_flag}\n"
            )
        report += "\n"
    return report




# Define acceptable ranges for sensors
VALID_RANGES = {
    "vibration": (0, 10),
    "temperature": (27, 80),
    "rpm": (300, 450),
}

rolling_data = {}

def convert_to_sri_lankan_time(utc_timestamp):
    try:
        normalized_timestamp = utc_timestamp[:26] + 'Z'
        utc_time = datetime.strptime(normalized_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        sri_lanka_tz = pytz.timezone("Asia/Colombo")
        return utc_time.replace(tzinfo=pytz.utc).astimezone(sri_lanka_tz)
    except ValueError as ve:
        raise ValueError(f"Failed to parse timestamp '{utc_timestamp}': {ve}")


# Additional state tracking
anomaly_tracker = {
    "vibration": deque(maxlen=30),
    "temperature": deque(maxlen=30),
    "rpm": deque(maxlen=30),
}

async def process_event(event_body):
    # Convert timestamp
    azure_timestamp = event_body.get("timestamp")
    sri_lankan_time = convert_to_sri_lankan_time(azure_timestamp) if azure_timestamp else None

    # Extract raw data
    raw_data = {
        "vibration_1": event_body.get("vibration_1"),
        "vibration_2": event_body.get("vibration_2"),
        "vibration_3": event_body.get("vibration_3"),
        "temperature": event_body.get("temperature"),
        "rpm": event_body.get("rpm_1"),

        # "vibration_1_null_flag": event_body.get("vibration_1_null_flag"),
        # "vibration_2_null_flag": event_body.get("vibration_2_null_flag"),
        # "vibration_3_null_flag": event_body.get("vibration_3_null_flag"),
        # "temperature_null_flag": event_body.get("temperature_null_flag"),
        # "rpm_1_null_flag": event_body.get("rpm_1_null_flag"),

        # "vibration_anomaly_flag": event_body.get("vibration_anomaly_flag"),
        # "temperature_anomaly_flag": event_body.get("temperature_anomaly_flag"),
        # "rpm_anomaly_flag": event_body.get("rpm_anomaly_flag"),
        # "overall_health_status": event_body.get("overall_health_status")
    }

    processed_data = {}

    # Anomaly Handling
    # for sensor, value in raw_data.items():
    #     if sensor not in rolling_data:
    #         rolling_data[sensor] = deque(maxlen=30) # 5 min rolling window (30 samples every 10 seconds)
    #     rolling_data[sensor].append(value)
    #     #rolling_data[sensor] = handle_outliers(list(rolling_data[sensor]))
    #     cleaned_data = handle_outliers(list(rolling_data[sensor]))
    #     processed_data[sensor] = cleaned_data[-1]  # Use the latest processed value
    # Anomaly Handling with validation and correction
    for sensor, value in raw_data.items():
        if value is not None:  # Only process non-null values
            sensor_type = sensor.split('_')[0]  # Extract base sensor type
            if sensor_type in VALID_RANGES:
                if sensor not in rolling_data:
                    rolling_data[sensor] = deque(maxlen=30)  # Rolling window
                rolling_data[sensor].append(value)
                range_min, range_max = VALID_RANGES[sensor_type]
                corrected_values = validate_and_correct(list(rolling_data[sensor]), range_min, range_max)
                processed_data[sensor] = corrected_values[-1]  # Use latest corrected value

    # Compute statistics
    stats_data = {sensor: compute_statistics(values) for sensor, values in rolling_data.items()}

    raw_data["vibration_1_null_flag"] = event_body.get("vibration_1_null_flag")
    raw_data["vibration_2_null_flag"] = event_body.get("vibration_2_null_flag")
    raw_data["vibration_3_null_flag"] = event_body.get("vibration_3_null_flag")
    raw_data["temperature_null_flag"] = event_body.get("temperature_null_flag")
    raw_data["rpm_1_null_flag"] = event_body.get("rpm_1_null_flag")

    raw_data["vibration_anomaly_flag"] = event_body.get("vibration_anomaly_flag")
    raw_data["temperature_anomaly_flag"] = event_body.get("temperature_anomaly_flag")
    raw_data["rpm_anomaly_flag"] = event_body.get("rpm_anomaly_flag")
    raw_data["overall_health_status"] = event_body.get("overall_health_status")

    # Anomaly detection logic
    # for flag_key, value in {
    #     "vibration_anomaly_flag": raw_data.get("vibration_anomaly_flag"),
    #     "temperature_anomaly_flag": raw_data.get("temperature_anomaly_flag"),
    #     "rpm_anomaly_flag": raw_data.get("rpm_anomaly_flag"),
    # }.items():
    #     if value != "Normal":
    #         anomaly_tracker[flag_key.split("_")[0]].append(value)
    #     else:
    #         anomaly_tracker[flag_key.split("_")[0]].append("Normal")

    # # Check if anomaly persists for > 50% of data in the rolling window
    # for sensor, tracker in anomaly_tracker.items():
    #     counts = Counter(tracker)
    #     if counts.get("Anomaly", 0) / len(tracker) > 0.5:
    #         message = f"Anomaly detected in {sensor.upper()} for more than 50% of recent readings."
    #         send_anomaly_email(f"{sensor.upper()} Anomaly Warning", message)



    null_flags = {}
    anomaly_flags = {}
    null_flags["vibration_1_null_flag"] = event_body.get("vibration_1_null_flag")
    null_flags["vibration_2_null_flag"] = event_body.get("vibration_2_null_flag")
    null_flags["vibration_3_null_flag"] = event_body.get("vibration_3_null_flag")
    null_flags["temperature_null_flag"] = event_body.get("temperature_null_flag")
    null_flags["rpm_1_null_flag"] = event_body.get("rpm_1_null_flag")

    anomaly_flags["vibration_anomaly_flag"] = event_body.get("vibration_anomaly_flag")
    anomaly_flags["temperature_anomaly_flag"] = event_body.get("temperature_anomaly_flag")
    anomaly_flags["rpm_anomaly_flag"] = event_body.get("rpm_anomaly_flag")

    # Anomaly or Null detection
    anomalies_detected = [
        key for key, value in anomaly_flags.items() if value == "Anomaly"
    ]
    null_detected = [
        key for key, value in null_flags.items() if value
    ]

    if anomalies_detected or null_detected:
        anomaly_record = {
            "timestamp": sri_lankan_time.isoformat(),
            "sensor_data": raw_data,
            "anomalies": anomalies_detected,
            "nulls": null_detected
        }
        await store_anomaly_record(anomaly_record["timestamp"], anomaly_record["anomalies"], anomaly_record["nulls"], anomaly_record["sensor_data"])

        # Check for email threshold
        # total_checks = len(raw_data["anomaly_flags"]) + len(raw_data["null_flags"])
        # anomaly_count = len(anomalies_detected) + len(null_detected)
        # if anomaly_count / total_checks > 0.5:
        #     send_detailed_anomaly_email(
        #         "Anomaly Alert Report",
        #         f"More than 50% anomalies detected.\n\nDetails:\n{anomaly_record}"
        #     )

    






    # Add current readings to the rolling buffer
    for sensor in ["vibration_1", "vibration_2", "vibration_3", "temperature", "rpm"]:
        value = event_body.get(sensor)
        null_flag = event_body.get(f"{sensor}_null_flag", False)
        anomaly_flag = event_body.get(f"{sensor.split('_')[0]}_anomaly_flag", False)

        rolling_buffer[sensor].append((sri_lankan_time, value, null_flag, anomaly_flag))

    # Check if >50% of the data in the last 5 minutes are anomalies or nulls
    total_readings = 0
    anomaly_count = 0

    for sensor, readings in rolling_buffer.items():
        for _, _, null_flag, anomaly_flag in readings:
            total_readings += 1
            if null_flag or anomaly_flag:
                anomaly_count += 1

    # If anomalies or nulls exceed 50%, send an email
    if total_readings > 0 and (anomaly_count / total_readings) > 0.5:
        report = generate_anomaly_report(rolling_buffer)
        subject = "Critical Alert: High Anomaly Count Detected"
        #send_anomaly_email(subject, report)








    stats_data["vibration_1_null_flag"] = event_body.get("vibration_1_null_flag")
    stats_data["vibration_2_null_flag"] = event_body.get("vibration_2_null_flag")
    stats_data["vibration_3_null_flag"] = event_body.get("vibration_3_null_flag")
    stats_data["temperature_null_flag"] = event_body.get("temperature_null_flag")
    stats_data["rpm_1_null_flag"] = event_body.get("rpm_1_null_flag")

    stats_data["vibration_anomaly_flag"] = event_body.get("vibration_anomaly_flag")
    stats_data["temperature_anomaly_flag"] = event_body.get("temperature_anomaly_flag")
    stats_data["rpm_anomaly_flag"] = event_body.get("rpm_anomaly_flag")
    stats_data["overall_health_status"] = event_body.get("overall_health_status")
    
    return {
        "timestamp": sri_lankan_time.isoformat(),
        #"raw_data": raw_data,
        "processed_data": processed_data,
        "statistics": stats_data,
    }
