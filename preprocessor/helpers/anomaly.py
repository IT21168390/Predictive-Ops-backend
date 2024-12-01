from typing import List
import numpy as np
import statistics

def handle_anomalies(data: List[float], threshold_min: float, threshold_max: float) -> List[float]:
    valid_data = [d for d in data if threshold_min <= d <= threshold_max]
    if not valid_data:  # All values are anomalous
        return [float('nan')] * len(data)
    mean_value = statistics.mean(valid_data)
    return [mean_value if d < threshold_min or d > threshold_max else d for d in data]

def handle_outliers(data_list: List[float], method="z_score", threshold=3) -> List[float]:
    data_array = np.array(data_list)
    if method == "z_score":
        mean = np.mean(data_array)
        std = np.std(data_array)
        z_scores = (data_array - mean) / std
        return [
            value if abs(z) <= threshold else mean
            for value, z in zip(data_array, z_scores)
        ]
    elif method == "iqr":
        q1, q3 = np.percentile(data_array, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return [
            value if lower_bound <= value <= upper_bound else np.median(data_array)
            for value in data_array
        ]
    return data_list


def validate_and_correct(data: List[float], range_min: float, range_max: float, outlier_method="z_score") -> List[float]:
    # Step 1: Handle anomalies outside acceptable range
    corrected_data = handle_anomalies(data, range_min, range_max)
    # Step 2: Handle statistical outliers
    corrected_data = handle_outliers(corrected_data, method=outlier_method)
    return corrected_data