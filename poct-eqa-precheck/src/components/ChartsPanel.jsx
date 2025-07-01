import React from 'react';
import { Line, Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function ChartsPanel({ data }) {
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

  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-bold mb-2">Trend</h3>
        <Line data={lineData} />
      </div>
      <div>
        <h3 className="font-bold mb-2">Altman-Bland Plot</h3>
        <Scatter data={altmanConfig} />
      </div>
    </div>
  );
}
