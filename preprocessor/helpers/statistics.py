import numpy as np
from typing import List, Dict

def compute_statistics(data_list: List[float]) -> Dict[str, float]:
    data_array = np.array(data_list)
    return {
        "mean": np.mean(data_array),
        "median": np.median(data_array),
        "std_dev": np.std(data_array),
        "min": np.min(data_array),
        "max": np.max(data_array),
        "range": np.ptp(data_array),
    }

