import React from 'react';
import { BoxPlot } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';
import 'chartjs-chart-box-and-violin-plot/build/Chart.BoxPlot.js';
import { buildBoxPlotData } from '../utils/chartData.js';

ChartJS.register(CategoryScale, LinearScale, Tooltip, Legend);

/** Box plot showing distribution of usage hours per operator */
function BoxPlotChart({ events }) {
  if (!events.length) return null;
  const { labels, data } = buildBoxPlotData(events);
  const dataset = {
    labels,
    datasets: [
      {
        label: 'Usage Hours',
        backgroundColor: '#60a5fa',
        borderColor: '#1d4ed8',
        borderWidth: 1,
        outlierColor: '#a855f7',
        padding: 10,
        itemRadius: 0,
        data,
      },
    ],
  };
  const options = { responsive: true, plugins: { legend: { position: 'top' } } };
  return (
    <div className="my-4">
      <h2 className="text-xl font-semibold mb-2">Usage Box Plot</h2>
      <BoxPlot data={dataset} options={options} />
    </div>
  );
}
export default BoxPlotChart;
