import React, { useRef } from 'react';
import { Line, Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
import html2canvas from 'html2canvas';
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function ChartsPanel({ data }) {
  const trendRef = useRef(null);
  const altmanRef = useRef(null);
  const dates = data.map(r => r.test_date);
  const measured = data.map(r => r.measured_value);
  const target = data.map(r => r.target_value);
  const altmanData = data.map(r => ({ x: (r.measured_value + r.target_value) / 2, y: r.measured_value - r.target_value }));

  const lineData = {
    labels: dates,
    datasets: [
      { label: 'Measured', data: measured, borderColor: 'blue' },
      { label: 'Target', data: target, borderColor: 'green' },
    ],
  };

  const altmanConfig = {
    datasets: [
      {
        label: 'Altman-Bland',
        data: altmanData,
        borderColor: 'red',
        showLine: false,
      },
    ],
  };

  const downloadPNG = async (ref, name) => {
    if (!ref.current) return;
    const canvas = await html2canvas(ref.current);
    const link = document.createElement('a');
    link.download = `${name}.png`;
    link.href = canvas.toDataURL();
    link.click();
  };

  return (
    <div className="space-y-6">
      <div ref={trendRef} className="relative chart-container">
        <h3 className="font-bold mb-2">Trend</h3>
        <Line data={lineData} />
        <button
          className="absolute top-0 right-0 text-sm underline"
          onClick={() => downloadPNG(trendRef, 'trend')}
        >
          Download PNG
        </button>
      </div>
      <div ref={altmanRef} className="relative chart-container">
        <h3 className="font-bold mb-2">Altman-Bland Plot</h3>
        <Scatter data={altmanConfig} />
        <button
          className="absolute top-0 right-0 text-sm underline"
          onClick={() => downloadPNG(altmanRef, 'altman')}
        >
          Download PNG
        </button>
      </div>
    </div>
  );
}
