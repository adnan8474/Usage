# CodeShare Watchtower

A lightweight in-browser tool to detect barcode (Operator ID) sharing in point-of-care testing logs. It provides basic analytics including operator timelines, device/location matrices, usage box plots and an hourly heatmap.

This project uses **React**, **Vite** and **Tailwind CSS** and runs entirely client side. It loads CSV files with the following columns:

```
Timestamp,Operator ID,Device,Location,Test Type
```

The app demonstrates three detection approaches:

1. **Temporal & Spatial Collision** – flags the same operator within 15 minutes at different devices or locations.
2. **Unusual Usage Pattern** – builds a simple usage profile and highlights events outside ±2 standard deviations of typical hours.
3. **Device–Ward Matrix Violation** – marks rare device/location combinations.

A sample dataset generator is included to simulate anomalies. CSV or PDF reports of flagged events can be downloaded for review.

Run locally with:

```bash
npm install
npm run dev
```

This is still a minimal prototype and not a production ready solution. Additional charts and validations should be added to reach the full feature set described in the project brief.
