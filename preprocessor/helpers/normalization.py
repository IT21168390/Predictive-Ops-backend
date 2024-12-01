def normalize(value, min_value, max_value):
    """Normalize data to a 0-1 range."""
    return (value - min_value) / (max_value - min_value)
