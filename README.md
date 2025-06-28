# POCTIFY Usage Intelligence

Streamlit app for monitoring point-of-care testing (POCT) usage. Upload CSV or Excel files using the template provided in `usage_intelligence/data/template.csv`.

Run locally with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app flags rapid succession tests, location conflicts, hourly density anomalies, device hopping, and shift consistency issues. It provides interactive charts and downloadable reports. Only non-patient data is allowed.
