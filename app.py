from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import pandas as pd
import joblib

app = Flask(__name__)

# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "fraud_detector_xgb_model.joblib"

model = joblib.load(MODEL_PATH)


# The exact features used when training the XGBoost model
MODEL_FEATURES = (
    ["Time"]
    + [f"V{i}" for i in range(1, 29)]
    + ["Amount"]
)


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------
# CLEAN CSV
# ---------------------------------------------------------

def clean_dataframe(df):

    # Remove unnamed/index columns created by Excel or pandas
    columns_to_remove = []

    for column in df.columns:

        column_string = str(column).strip().lower()

        if (
            column_string.startswith("unnamed:")
            or column_string in ["index", "id"]
        ):
            columns_to_remove.append(column)

    if columns_to_remove:
        df = df.drop(columns=columns_to_remove)

    # Remove spaces from column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# ---------------------------------------------------------
# CHECK ORIGINAL XGBOOST FORMAT
# ---------------------------------------------------------

def has_xgboost_features(df):

    required = set(MODEL_FEATURES)

    available = set(df.columns)

    return required.issubset(available)


# ---------------------------------------------------------
# XGBOOST PREDICTION
# ---------------------------------------------------------

def predict_xgboost(df):

    # Keep only the features used during training
    X = df[MODEL_FEATURES].copy()

    # Convert values to numbers
    for column in MODEL_FEATURES:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    # Check missing values
    if X.isnull().any().any():

        bad_columns = X.columns[
            X.isnull().any()
        ].tolist()

        raise ValueError(
            "Invalid or missing numeric values in: "
            + ", ".join(bad_columns)
        )

    # Real XGBoost probability
    probabilities = model.predict_proba(X)[:, 1]

    results = []

    for probability in probabilities:

        fraud_probability = round(
            float(probability) * 100,
            2
        )

        legitimate_probability = round(
            100 - fraud_probability,
            2
        )

        if fraud_probability >= 70:
            risk = "High"

        elif fraud_probability >= 40:
            risk = "Medium"

        else:
            risk = "Low"

        if probability >= 0.5:

            prediction = (
                "Fraudulent Transaction"
            )

        else:

            prediction = (
                "Legitimate Transaction"
            )

        results.append({

            "prediction": prediction,

            "fraud_probability":
                fraud_probability,

            "legitimate_probability":
                legitimate_probability,

            "risk": risk,

            "method": "XGBoost"
        })

    return results


# ---------------------------------------------------------
# YOUR CUSTOM TRANSACTION FORMAT
# ---------------------------------------------------------

def has_custom_features(df):

    custom_features = {

        "Amount",

        "Transactions_Last_24h",

        "International_Transaction",

        "New_Device",

        "Unusual_Time"
    }

    return custom_features.issubset(
        set(df.columns)
    )


# ---------------------------------------------------------
# CUSTOM FORMAT PREDICTION
# ---------------------------------------------------------

def predict_custom_format(df):

    results = []

    for _, row in df.iterrows():

        score = 0.05

        # ---------------------------------------------
        # Amount
        # ---------------------------------------------

        try:

            amount = float(
                row["Amount"]
            )

            if amount > 1000:
                score += 0.15

            if amount > 5000:
                score += 0.20

        except:

            amount = 0


        # ---------------------------------------------
        # Transaction frequency
        # ---------------------------------------------

        try:

            transactions = float(
                row["Transactions_Last_24h"]
            )

            if transactions >= 10:
                score += 0.20

            elif transactions >= 5:
                score += 0.10

        except:

            transactions = 0


        # ---------------------------------------------
        # International transaction
        # ---------------------------------------------

        international = str(
            row["International_Transaction"]
        ).strip().lower()

        if international in [
            "yes",
            "true",
            "1",
            "international"
        ]:

            score += 0.15


        # ---------------------------------------------
        # New device
        # ---------------------------------------------

        new_device = str(
            row["New_Device"]
        ).strip().lower()

        if new_device in [
            "yes",
            "true",
            "1",
            "new"
        ]:

            score += 0.15


        # ---------------------------------------------
        # Unusual time
        # ---------------------------------------------

        unusual_time = str(
            row["Unusual_Time"]
        ).strip().lower()

        if unusual_time in [
            "yes",
            "true",
            "1",
            "unusual"
        ]:

            score += 0.15


        score = min(
            max(score, 0.01),
            0.99
        )


        fraud_probability = round(
            score * 100,
            2
        )

        legitimate_probability = round(
            100 - fraud_probability,
            2
        )


        if fraud_probability >= 70:

            risk = "High"

        elif fraud_probability >= 40:

            risk = "Medium"

        else:

            risk = "Low"


        prediction = (

            "Fraudulent Transaction"

            if score >= 0.5

            else "Legitimate Transaction"
        )


        results.append({

            "prediction": prediction,

            "fraud_probability":
                fraud_probability,

            "legitimate_probability":
                legitimate_probability,

            "risk": risk,

            "method":
                "Transaction Risk Scoring"
        })


    return results


# ---------------------------------------------------------
# CSV PREDICTION API
# ---------------------------------------------------------

@app.route(
    "/predict_csv",
    methods=["POST"]
)
def predict_csv():

    # Check file
    if "file" not in request.files:

        return jsonify({
            "error":
                "Please upload a CSV file."
        }), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify({
            "error":
                "No file selected."
        }), 400


    if not file.filename.lower().endswith(".csv"):

        return jsonify({
            "error":
                "Only CSV files are supported."
        }), 400


    try:

        # Read CSV
        dataframe = pd.read_csv(file)


        if dataframe.empty:

            return jsonify({
                "error":
                    "The CSV file is empty."
            }), 400


        # Clean columns
        dataframe = clean_dataframe(
            dataframe
        )


        # Limit upload size
        dataframe = dataframe.head(1000)


        # -------------------------------------------------
        # FORMAT 1
        # Original XGBoost dataset
        # -------------------------------------------------

        if has_xgboost_features(
            dataframe
        ):

            results = predict_xgboost(
                dataframe
            )

            method = (
                "Trained XGBoost Model"
            )


        # -------------------------------------------------
        # FORMAT 2
        # Custom transaction dataset
        # -------------------------------------------------

        elif has_custom_features(
            dataframe
        ):

            results = predict_custom_format(
                dataframe
            )

            method = (
                "Transaction Risk Scoring"
            )


        # -------------------------------------------------
        # UNKNOWN FORMAT
        # -------------------------------------------------

        else:

            required_xgb = (
                "Time, V1-V28, Amount"
            )

            required_custom = (
                "Amount, "
                "Transactions_Last_24h, "
                "International_Transaction, "
                "New_Device, "
                "Unusual_Time"
            )

            return jsonify({

                "error":
                    "CSV format not recognized.",

                "message":
                    "Use either the original credit-card "
                    "format or the supported transaction format.",

                "xgboost_format":
                    required_xgb,

                "custom_format":
                    required_custom,

                "columns_found":
                    list(dataframe.columns)

            }), 400


        return jsonify({

            "success": True,

            "count":
                len(results),

            "method":
                method,

            "results":
                results

        })


    except Exception as error:

        return jsonify({

            "error":
                "Prediction failed.",

            "details":
                str(error)

        }), 500


# ---------------------------------------------------------
# SAMPLE FILES
# ---------------------------------------------------------

@app.route(
    "/sample_legitimate_transaction.csv"
)
def sample_legitimate():

    return send_from_directory(
        BASE_DIR,
        "sample_legitimate_transaction.csv"
    )


@app.route(
    "/sample_fraud_transaction.csv"
)
def sample_fraud():

    return send_from_directory(
        BASE_DIR,
        "sample_fraud_transaction.csv"
    )


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )

