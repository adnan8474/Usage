import React from 'react';

export default function SummaryPanel({ stats }) {
  const warn = stats.cv > 5;
  return (
    <div className={`p-4 rounded shadow ${warn ? 'bg-yellow-100' : 'bg-green-100'}`}> 
      <p><strong>Analyte:</strong> {stats.analyte}</p>
      <p><strong>Devices:</strong> {stats.devices}</p>
      <p><strong>Mean:</strong> {stats.mean.toFixed(2)}</p>
      <p><strong>SD:</strong> {stats.sd.toFixed(2)}</p>
      <p><strong>CV%:</strong> {stats.cv.toFixed(2)}</p>
      {warn && <p className="text-red-600">Warning: CV% &gt; 5%</p>}
    </div>
  );
}
