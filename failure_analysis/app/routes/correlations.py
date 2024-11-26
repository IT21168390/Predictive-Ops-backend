from flask import Blueprint, jsonify
from app.utils.data_loader import load_dataset
import pandas as pd

bp = Blueprint('correlations', __name__, url_prefix='/correlations')


df = pd.read_csv('PredictiveMaintenance_mod.csv')
df.drop(['rpm_anomaly_flag','vibration_anomaly_flag','temperature_anomaly_flag','Target', 'Failure Type', 'Failure Flag' ] , axis=1 , inplace=True)
correlation_matrix = df.corr()

@bp.route("/correlation_matrix", methods=["GET"])
def get_correlation_matrix():
    return jsonify(correlation_matrix.to_dict())