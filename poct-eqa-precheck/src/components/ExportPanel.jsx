import React from 'react';
import { exportCSV, exportPDF } from '../utils/exporters.js';

export default function ExportPanel({ data, stats }) {
  return (
    <div className="space-x-4">
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded"
        onClick={() => exportCSV(data)}
      >
        Export as CSV
      </button>
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded"
        onClick={() => exportPDF(data, stats)}
      >
        Export PDF Report
      </button>
    </div>
  );
}
