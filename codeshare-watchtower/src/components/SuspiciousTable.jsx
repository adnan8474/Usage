import React from 'react';

function SuspiciousTable({ flags }) {
  return (
    <table className="min-w-full text-sm bg-white dark:bg-gray-700">
      <thead>
        <tr>
          <th className="px-2 py-1">Operator ID</th>
          <th className="px-2 py-1">Description</th>
        </tr>
      </thead>
      <tbody>
        {flags.map((f, idx) => (
          <tr key={idx} className="border-t">
            <td className="px-2 py-1">{f.operator}</td>
            <td className="px-2 py-1">
              {f.current && (
                <span>
                  Collision at {f.current.location} / {f.compare.location}
                </span>
              )}
              {f.event && <span>Unusual hour {f.event.timestamp.format('HH:mm')}</span>}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default SuspiciousTable;
