from flask import Flask, request, jsonify
import pickle
import numpy as np
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# Load the trained model
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Load the MinMaxScaler
with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Load the failure type mapping
failure_type_mapping = {
    0: "No Failure",
    1: "Trimmer Bearing Fault",
    2: "Drill Issue",
    # Add more failure types if necessary based on your model's output
}

# Preprocess the input data and make predictions
def preprocess_and_predict(processed_data):
    try:
        # Extract relevant features from the incoming data
        features = [
            processed_data["vibration_1"],
            processed_data["vibration_2"],
            processed_data["vibration_3"],
            processed_data["temperature"],
            processed_data["rpm"]
        ]
        
        # Scale the input features using the same scaler used during training
        scaled_features = scaler.transform([features])

        # Predict using the trained model (binary classification: 0 or 1)
        predicted_target = model.predict(scaled_features)[0]

        # Use the predicted target to get the failure type from the mapping
        predicted_failure_type = failure_type_mapping.get(predicted_target, "Unknown Failure")

        return {
            "predicted_target": int(predicted_target),
            "predicted_failure_type": predicted_failure_type
        }
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return {"error": str(e)}

# Flask route to receive real-time data
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse the incoming JSON data
        input_data = request.json

        # Extract the 'processed_data' from the payload
        processed_data = input_data.get("processed_data", {})
        if not processed_data:
            return jsonify({"error": "No processed_data found in the request"}), 400

        # Run the prediction function
        prediction = preprocess_and_predict(processed_data)

        

        # Return the prediction as a JSON response
        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask route for health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running"}), 200

# Run the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
