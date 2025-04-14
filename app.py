from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Crop-specific moisture thresholds (in %)
CROP_THRESHOLDS = {
    'wheat': 30,
    'rice': 40,
    'corn': 35,
    'soybean': 32,
    'cotton': 28
}

# Simple decision tree for irrigation prediction
def predict_irrigation(soil_moisture, humidity, temperature, crop_type):
    # Get crop-specific threshold
    threshold = CROP_THRESHOLDS[crop_type]
    
    # Basic rules for irrigation prediction
    if soil_moisture < threshold:
        # If soil moisture is below threshold, check other conditions
        if temperature > 30 and humidity < 60:
            return True  # Hot and dry conditions
        elif soil_moisture < threshold - 5:
            return True  # Significantly below threshold
        else:
            return False
    else:
        return False

def calculate_water_amount(soil_moisture, crop_type):
    threshold = CROP_THRESHOLDS[crop_type]
    if soil_moisture < threshold:
        return round((threshold - soil_moisture) * 2, 1)  # 2mm per % below threshold
    return 0

@app.route('/')
def index():
    return send_from_directory('.', 'mlw.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        soil_moisture = float(data['soilMoisture'])
        humidity = float(data['humidity'])
        temperature = float(data['temperature'])
        crop_type = data['cropType']

        # Validate inputs
        if not (0 <= soil_moisture <= 100):
            return jsonify({'error': 'Soil moisture must be between 0 and 100'}), 400
        if not (0 <= humidity <= 100):
            return jsonify({'error': 'Humidity must be between 0 and 100'}), 400
        if crop_type not in CROP_THRESHOLDS:
            return jsonify({'error': 'Invalid crop type'}), 400

        # Make prediction using simple decision tree
        needs_irrigation = predict_irrigation(soil_moisture, humidity, temperature, crop_type)
        
        # Calculate water amount if irrigation is needed
        water_amount = calculate_water_amount(soil_moisture, crop_type) if needs_irrigation else 0

        return jsonify({
            'irrigationNeeded': needs_irrigation,
            'waterAmount': water_amount,
            'cropType': crop_type,
            'soilMoisture': soil_moisture,
            'humidity': humidity,
            'temperature': temperature
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 