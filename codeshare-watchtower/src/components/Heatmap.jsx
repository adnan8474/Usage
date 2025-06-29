import React from 'react';
import { buildHourlyCounts } from '../utils/chartData.js';

/** Hourly heatmap representing overall activity */
function Heatmap({ events }) {
  if (!events.length) return null;
  const counts = buildHourlyCounts(events);
  const max = Math.max(...counts);
  const colour = (c) => {
    if (!max) return 'bg-gray-200';
    const ratio = c / max;
    if (ratio > 0.75) return 'bg-red-500';
    if (ratio > 0.5) return 'bg-orange-400';
    if (ratio > 0.25) return 'bg-yellow-300';
    return 'bg-green-200';
  };
  return (
    <div className="my-4">
      <h2 className="text-xl font-semibold mb-2">Hourly Heatmap</h2>
      <div className="grid gap-1" style={{ gridTemplateColumns: 'repeat(24, 1fr)' }}>
        {counts.map((c, i) => (
          <div
            key={i}
            className={`h-8 text-center text-xs flex items-center justify-center ${colour(c)}`}
          >
            {i}
          </div>
        ))}
      </div>
    </div>
  );
}
export default Heatmap;
