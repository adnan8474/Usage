# POCTIFY Usage Intelligence

Streamlit app for monitoring point-of-care testing (POCT) usage. Upload CSV or Excel files using the template provided in `usage_intelligence/data/template.csv`.

Run locally with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app flags barcode sharing and suspicious operator behaviour using probabilistic scoring. It includes heatmaps, density plots and operator timelines. Only anonymised, non-patient data should be used.

**Note:** If timestamp parsing fails you will see the offending line numbers. Do not share patient or staff names in uploads.
