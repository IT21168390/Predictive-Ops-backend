import pandas as pd

def load_dataset(filepath='dataset.csv'):
    df = pd.read_csv(filepath)
    return df