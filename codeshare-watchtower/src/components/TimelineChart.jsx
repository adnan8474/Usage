import React from 'react';
import { Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  TimeScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js';
import 'chartjs-adapter-dayjs';
import { buildTimelineSeries } from '../utils/chartData.js';

ChartJS.register(TimeScale, LinearScale, PointElement, Tooltip, Legend);

/** Timeline scatter plot showing operator activity over time */
function TimelineChart({ events }) {
  if (!events.length) return null;
  const colors = [
    '#2563eb',
    '#059669',
    '#ef4444',
    '#a855f7',
    '#f59e0b',
  ];
  const series = buildTimelineSeries(events);
  const data = {
    datasets: series.map((s, idx) => ({
      label: s.label,
      data: s.data,
      backgroundColor: colors[idx % colors.length],
    })),
  };
  const options = {
    responsive: true,
    scales: {
      x: { type: 'time', title: { display: true, text: 'Time' } },
      y: {
        ticks: {
          callback: (v) => (series[v] ? series[v].label : v),
        },
        title: { display: true, text: 'Operator' },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (ctx) => ctx.raw.x.toLocaleString(),
        },
      },
    },
  };
  return (
    <div className="my-4">
      <h2 className="text-xl font-semibold mb-2">Timeline</h2>
      <Scatter data={data} options={options} />
    </div>
  );
}
export default TimelineChart;
