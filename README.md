# POCTIFY Usage Intelligence

Streamlit app for monitoring point-of-care testing (POCT) usage. Upload CSV or Excel files using the template provided in `usage_intelligence/data/template.csv`.

Features include:

- Probabilistic flagging of barcode sharing and location conflicts
- Interactive heatmaps, hourly trends and device timelines
- Sidebar filters for operator, device, location, test type and date range
- Downloadable flagged data and scores
- Optional export of key plots via the sidebar

Run locally with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Optionally place a `POCTIFY Logo.png` file in the repository root to display the logo in the sidebar.

The app flags barcode sharing and suspicious operator behaviour using probabilistic scoring. It includes heatmaps, density plots and operator timelines. Only anonymised, non-patient data should be used.

The sidebar optionally shows a `POCTIFY Logo.png` image if present in the repository root and provides filter controls to limit analysis by operator, location, device, test type, date range and minimum suspicion score.

**Note:** If timestamp parsing fails you will see the offending line numbers. Do not share patient or staff names in uploads.
