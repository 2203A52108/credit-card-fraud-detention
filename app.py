from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

def fraud_probability(amount, hour, distance, velocity, international):
    # Demo scoring layer for the UI. Replace with the trained model artifact
    # when the original dataset/model is added.
    score = 0.08
    if amount > 1000: score += min((amount-1000)/5000, 0.30)
    if amount > 5000: score += 0.15
    if hour < 5 or hour > 23: score += 0.12
    if distance > 500: score += 0.12
    if velocity > 5: score += min((velocity-5)*0.025, 0.18)
    if international: score += 0.12
    return max(0.01, min(score, 0.99))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    amount = float(data.get("amount", 0))
    hour = int(data.get("hour", 12))
    distance = float(data.get("distance", 0))
    velocity = float(data.get("velocity", 0))
    international = bool(data.get("international", False))

    probability = fraud_probability(amount, hour, distance, velocity, international)
    fraud_pct = round(probability * 100, 1)
    legit_pct = round(100 - fraud_pct, 1)
    is_fraud = probability >= 0.50

    return jsonify({
        "prediction": "Fraudulent Transaction" if is_fraud else "Legitimate Transaction",
        "fraud_probability": fraud_pct,
        "legitimate_probability": legit_pct,
        "risk": "High" if fraud_pct >= 70 else "Medium" if fraud_pct >= 40 else "Low"
    })

if __name__ == "__main__":
    app.run(debug=True)
