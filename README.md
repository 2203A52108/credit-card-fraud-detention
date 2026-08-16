# Credit Card Fraud Detection Web App

A GitHub-ready Flask web interface for analyzing credit-card transaction risk.

## Features
- Transaction risk analysis
- Fraud probability percentage
- Legitimate probability percentage
- Low/Medium/High risk level
- Responsive dashboard UI
- Flask API endpoint

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Important
The included scoring layer is a demo interface. For a production ML project, train the model on the credit-card fraud dataset and replace `fraud_probability()` in `app.py` with the saved model's `predict_proba()` output. Do not represent the demo score as a trained-model probability.

## Deployment
For Render or another Python host, use:

```bash
gunicorn app:app
```
