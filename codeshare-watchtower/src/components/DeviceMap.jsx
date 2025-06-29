import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { buildDeviceLocationMatrix } from '../utils/chartData.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

/** Stacked bar chart showing device usage per ward */
function DeviceMap({ events }) {
  if (!events.length) return null;
  const matrix = buildDeviceLocationMatrix(events);
  const devices = Object.keys(matrix);
  const locations = Array.from(new Set(events.map(e => e.location)));
  const colors = ['#60a5fa', '#fb923c', '#f87171', '#a78bfa'];
  const data = {
    labels: devices,
    datasets: locations.map((loc, idx) => ({
      label: loc,
      data: devices.map(d => matrix[d][loc] || 0),
      backgroundColor: colors[idx % colors.length],
    })),
  };
  const options = { responsive: true, plugins: { legend: { position: 'top' } } };
  return (
    <div className="my-4">
      <h2 className="text-xl font-semibold mb-2">Device-Location Matrix</h2>
      <Bar data={data} options={options} />
    </div>
  );
}
export default DeviceMap;
