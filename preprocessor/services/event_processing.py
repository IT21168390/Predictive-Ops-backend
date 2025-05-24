from collections import deque, defaultdict
from datetime import datetime
import pytz
from collections import Counter
from helpers.anomaly import handle_anomalies, handle_outliers, validate_and_correct
from helpers.statistics import compute_statistics
#from email_handler import send_anomaly_email, send_detailed_anomaly_email
from firebase_handler import store_anomaly_record
from email_handler import send_anomaly_email





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

def generate_anomaly_summary(rolling_buffer):
    """Generate summary table rows for email report."""
    summary = ""
    for sensor, readings in rolling_buffer.items():
        total = len(readings)
        anomalies = sum(1 for _, _, null_flag, anomaly_flag in readings if null_flag == 1 or anomaly_flag != "Normal")
        percentage = (anomalies / total) * 100 if total > 0 else 0
        summary += f"<tr><td>{sensor}</td><td>{total}</td><td>{anomalies}</td><td>{percentage:.2f}%</td></tr>"
    return summary




# Define acceptable ranges for sensors
VALID_RANGES = {
    "vibration": (0, 10),
    "temperature": (27, 60),
    "rpm": (100, 5000),
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
    }

    processed_data = {}

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
                processed_data[sensor] = float(corrected_values[-1])  # Use latest corrected value

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


    # Add current readings to the rolling buffer
    for sensor in ["vibration_1", "vibration_2", "vibration_3", "temperature", "rpm"]:
        value = event_body.get(sensor)
        null_flag = event_body.get(f"{sensor}_null_flag", False)
        anomaly_flag = event_body.get(f"{sensor.split('_')[0]}_anomaly_flag", False)

        rolling_buffer[sensor].append((sri_lankan_time, value, null_flag, anomaly_flag))

    # Count total readings and anomalies across all sensors
    all_readings = [reading for readings in rolling_buffer.values() for reading in readings]
    total_readings = len(all_readings)
    anomaly_count = sum(1 for _, _, null_flag, anomaly_flag in all_readings if null_flag==1 or anomaly_flag!="Normal")

    print(f"Total Readings: {total_readings}, Anomaly Count: {anomaly_count}")

    # Check if >60% of the data in the last 5 minutes are anomalies or nulls
    # Check anomaly percentage
    if total_readings >= 150:
        anomaly_percentage = (anomaly_count / total_readings) * 100
        print(f"Anomaly Percentage: {anomaly_percentage:.2f}%")

        if anomaly_percentage > 50:
            summary_table = generate_anomaly_summary(rolling_buffer)
            detailed_report = generate_anomaly_report(rolling_buffer)
            send_anomaly_email("Critical Alert: High Anomaly Count Detected", summary_table, detailed_report)

    # elif total_readings >= 30:
    #     total_readings -= 1







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
