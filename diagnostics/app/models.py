from datetime import datetime
from typing import Dict, List, Optional, Union

class PredictionModel:
    def __init__(self, model_name: str, model_type: str, features: List[str]):
        self.model_name = model_name
        self.model_type = model_type
        self.features = features
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class AnalyticsResult:
    def __init__(self, analysis_type: str, result: Dict[str, Union[float, str, List[float]]]):
        self.analysis_type = analysis_type
        self.result = result
        self.timestamp = datetime.utcnow()

class FailureAnalysis:
    def __init__(self, component: str, failure_type: str, probability: float):
        self.component = component
        self.failure_type = failure_type
        self.probability = probability
        self.timestamp = datetime.utcnow()

class PreprocessingConfig:
    def __init__(self, 
                 normalization: bool = True,
                 feature_selection: bool = True,
                 outlier_detection: bool = True,
                 missing_value_strategy: str = 'mean'):
        self.normalization = normalization
        self.feature_selection = feature_selection
        self.outlier_detection = outlier_detection
        self.missing_value_strategy = missing_value_strategy

class ModelMetrics:
    def __init__(self,
                 accuracy: float,
                 precision: float,
                 recall: float,
                 f1_score: float,
                 confusion_matrix: List[List[int]]):
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1_score = f1_score
        self.confusion_matrix = confusion_matrix
        self.timestamp = datetime.utcnow()

class DatasetMetadata:
    def __init__(self,
                 name: str,
                 features: List[str],
                 rows: int,
                 columns: int,
                 missing_values: Dict[str, int]):
        self.name = name
        self.features = features
        self.rows = rows
        self.columns = columns
        self.missing_values = missing_values
        self.created_at = datetime.utcnow()

class WebSocketMessage:
    def __init__(self,
                 message_type: str,
                 data: Dict[str, any],
                 status: str = 'success'):
        self.message_type = message_type
        self.data = data
        self.status = status
        self.timestamp = datetime.utcnow()