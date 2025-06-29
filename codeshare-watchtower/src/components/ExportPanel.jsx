import React from 'react';
import jsPDF from 'jspdf';

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

  const downloadPDF = () => {
    const doc = new jsPDF();
    doc.text('CodeShare Watchtower Report', 10, 10);
    flags.forEach((f, i) => {
      doc.text(`${i + 1}. ${f.operator}`, 10, 20 + i * 6);
    });
    doc.save('report.pdf');
  };

  return (
    <div className="mt-4 space-x-2">
      <button
        onClick={downloadCSV}
        className="px-3 py-2 bg-blue-500 text-white rounded"
      >
        Download CSV
      </button>
      <button
        onClick={downloadPDF}
        className="px-3 py-2 bg-purple-500 text-white rounded"
      >
        Download PDF
      </button>
    </div>
  );
}

export default ExportPanel;
