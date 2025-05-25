import pandas as pd
import os

def load_dataset(filepath=None):
    if filepath is None:
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dataset", "dataset.csv")
    return pd.read_csv(filepath)