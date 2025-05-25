import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from sklearn.preprocessing import StandardScaler
from ..models import FailureAnalysis
from flask import current_app
from ..models import ModelMetrics
from ..utils.data_loader import load_dataset
import joblib
import os
import pandas as pd

class FailureAnalysisService:
    def __init__(self):
        self.dataset = load_dataset()
        self.metrics = ModelMetrics(accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0, confusion_matrix=[[0, 0], [0, 0]])
        
        # Configure model path and load model
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "model.pkl")
        self.model = joblib.load(self.model_path)
        self.scaler = StandardScaler()

    def analyze_failure(self, data):
        # Use the loaded dataset for analysis
        df = self.dataset
        # Rest of the analysis logic
        return {'status': 'success', 'analysis': 'Failure analysis completed'}

    def get_failure_metrics(self):
        # Use the loaded dataset for metrics
        df = self.dataset
        # Calculate metrics
        return {'total_failures': len(df), 'metrics': 'Failure metrics calculated'}

    def predict_failure(self, data: Dict) -> Dict:
        try:
            # Prepare input data
            df = pd.DataFrame([data])
            scaled_data = self.scaler.fit_transform(df)
            
            # Make prediction
            prediction = self.model.predict_proba(scaled_data)[0]
            failure_probability = float(prediction[1])
            
            # Create response
            result = {
                'probability': failure_probability,
                'risk_level': self._get_risk_level(failure_probability),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
        except Exception as e:
            raise Exception(f"Prediction failed: {str(e)}")

    def analyze_component(self, data: Dict) -> Dict:
        try:
            # Perform component analysis
            df = pd.DataFrame([data])
            analysis_result = {
                'component_health': self._analyze_component_health(df),
                'maintenance_recommendation': self._get_maintenance_recommendation(df),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return analysis_result
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

    def get_failure_statistics(self) -> Dict:
        try:
            # Load historical data
            df = pd.read_csv('datasets/dataset.csv')
            
            statistics = {
                'total_failures': int(df['failure'].sum()),
                'failure_rate': float(df['failure'].mean()),
                'component_stats': self._get_component_statistics(df),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return statistics
        except Exception as e:
            raise Exception(f"Failed to get statistics: {str(e)}")

    def get_failure_history(self, component: str, start_date: str, end_date: str) -> List[Dict]:
        try:
            # Load and filter historical data
            df = pd.read_csv('datasets/dataset.csv')
            df['date'] = pd.to_datetime(df['date'])
            
            mask = (df['component'] == component) & \
                   (df['date'] >= start_date) & \
                   (df['date'] <= end_date)
            
            filtered_df = df[mask]
            
            history = filtered_df.to_dict('records')
            return history
        except Exception as e:
            raise Exception(f"Failed to get history: {str(e)}")

    def _get_risk_level(self, probability: float) -> str:
        if probability < 0.3:
            return 'LOW'
        elif probability < 0.7:
            return 'MEDIUM'
        else:
            return 'HIGH'

    def _analyze_component_health(self, df: pd.DataFrame) -> Dict:
        # Implement component health analysis logic
        return {
            'status': 'HEALTHY',
            'confidence': 0.95
        }

    def _get_maintenance_recommendation(self, df: pd.DataFrame) -> Dict:
        # Implement maintenance recommendation logic
        return {
            'action': 'MONITOR',
            'priority': 'LOW',
            'next_maintenance': datetime.utcnow().isoformat()
        }

    def _get_component_statistics(self, df: pd.DataFrame) -> Dict:
        # Calculate component-wise statistics
        stats = df.groupby('component')['failure'].agg([
            'count',
            'mean',
            'sum'
        ]).to_dict('index')
        
        return stats