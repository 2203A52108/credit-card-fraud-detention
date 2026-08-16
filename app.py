from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import pandas as pd
import joblib

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "fraud_detector_xgb_model.joblib"

model = joblib.load(MODEL_PATH)

FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


@app.route("/")
def index():
    return render_template("index.html")


def predict_frame(frame):
    missing = [column for column in FEATURES if column not in frame.columns]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    X = frame[FEATURES].apply(pd.to_numeric, errors="raise")

    probabilities = model.predict_proba(X)[:, 1]

    results = []

    for probability in probabilities:
        fraud_probability = round(float(probability) * 100, 2)
        legitimate_probability = round(100 - fraud_probability, 2)

        if fraud_probability >= 70:
            risk = "High"
        elif fraud_probability >= 40:
            risk = "Medium"
        else:
            risk = "Low"

        prediction = (
            "Fraudulent Transaction"
            if probability >= 0.5
            else "Legitimate Transaction"
        )

        results.append({
            "prediction": prediction,
            "fraud_probability": fraud_probability,
            "legitimate_probability": legitimate_probability,
            "risk": risk
        })

    return results


@app.route("/predict_csv", methods=["POST"])
def predict_csv():

    if "file" not in request.files:
        return jsonify({
            "error": "Please upload a CSV file."
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected."
        }), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({
            "error": "Only CSV files are supported."
        }), 400

    try:
        dataframe = pd.read_csv(file)

        if dataframe.empty:
            return jsonify({
                "error": "The CSV file is empty."
            }), 400

        # Prevent extremely large requests
        dataframe = dataframe.head(100)

        results = predict_frame(dataframe)

        return jsonify({
            "count": len(results),
            "results": results
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 400


@app.route("/sample_legitimate_transaction.csv")
def sample_legitimate():

    return send_from_directory(
        BASE_DIR,
        "sample_legitimate_transaction.csv",
        as_attachment=False
    )


@app.route("/sample_fraud_transaction.csv")
def sample_fraud():

    return send_from_directory(
        BASE_DIR,
        "sample_fraud_transaction.csv",
        as_attachment=False
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
