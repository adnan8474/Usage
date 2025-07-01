# POCT EQA Pre-Submission Analysis Platform

A lightweight, browser-based tool for analysing External Quality Assessment (EQA) results before submitting to providers. Upload CSV or Excel files to calculate statistics, view trend charts and export PDF/CSV reports.

## Setup

```bash
npm install
npm run dev
```

Build for deployment (e.g. Netlify):

```bash
npm run build
```

## File Format

The uploaded file should contain the following columns:

```
device_id,analyte,test_date,measured_value,target_value
```

A sample template is available in `public/template.csv`.
