from flask import Blueprint, request, jsonify
from ..utils.validation import validate_input_data

correlations_bp = Blueprint('correlations', __name__)