import numpy as np
from typing import List, Dict

def compute_statistics(data_list: List[float]) -> Dict[str, float]:
    data_array = np.array(data_list)
    return {
        "mean": float(np.mean(data_array)),
        "median": float(np.median(data_array)),
        "std_dev": float(np.std(data_array)),
        "min": float(np.min(data_array)),
        "max": float(np.max(data_array)),
        "range": float(np.ptp(data_array)),
    }

