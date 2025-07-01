import React from 'react';
import { groupByDevice, deviceStats } from '../utils/stats.js';

export default function StatsTable({ data }) {
  const grouped = groupByDevice(data);
  const rows = Object.keys(grouped).map((device) => ({
    device,
    ...deviceStats(grouped[device]),
  }));

  const color = (cv) => {
    if (cv < 5) return 'bg-green-100';
    if (cv < 10) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <table className="min-w-full text-sm">
      <thead>
        <tr>
          <th className="border px-2">Device</th>
          <th className="border px-2">Mean</th>
          <th className="border px-2">SD</th>
          <th className="border px-2">CV%</th>
          <th className="border px-2"># Tests</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.device} className={color(r.cv)}>
            <td className="border px-2">{r.device}</td>
            <td className="border px-2">{r.mean.toFixed(2)}</td>
            <td className="border px-2">{r.sd.toFixed(2)}</td>
            <td className="border px-2">{r.cv.toFixed(2)}</td>
            <td className="border px-2">{r.count}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
