import React from 'react';

function ExportPanel({ flags }) {
  const downloadCSV = () => {
    const headers = ['Operator','Detail'];
    const rows = flags.map(f => `${f.operator},Collision`);
    const blob = new Blob([headers.join(',') + '\n' + rows.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'report.csv';
    a.click();
  };

  return (
    <button onClick={downloadCSV} className="mt-4 px-3 py-2 bg-blue-500 text-white rounded">
      Download CSV
    </button>
  );
}

export default ExportPanel;
