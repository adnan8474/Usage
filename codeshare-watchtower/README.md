# CodeShare Watchtower

A lightweight in-browser tool to detect barcode (Operator ID) sharing in point-of-care testing logs.

This project uses **React**, **Vite** and **Tailwind CSS** and runs entirely client side. It loads CSV files with the following columns:

```
Timestamp,Operator ID,Device,Location,Test Type
```

The app demonstrates three detection approaches:

1. **Temporal & Spatial Collision** – flags the same operator within 15 minutes at different devices or locations.
2. **Unusual Usage Pattern** – builds a simple usage profile and highlights events outside ±2 standard deviations of typical hours.
3. **Device–Ward Matrix Violation** – marks rare device/location combinations.

A sample dataset generator is included to simulate anomalies. CSV reports of flagged events can be downloaded for review.

This is a minimal prototype and not a production ready solution. Further work is required to reach the 1200 line requirement and add rich visual analytics as described in the project brief.
