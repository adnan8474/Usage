import React from 'react';

export default function Instructions() {
  return (
    <div className="prose dark:prose-invert max-w-none">
      <h2>How to Use</h2>
      <ol className="list-decimal ml-6">
        <li>Prepare a CSV or XLSX file with the columns: <code>device_id</code>, <code>analyte</code>, <code>test_date</code>, <code>measured_value</code> and <code>target_value</code>.</li>
        <li>Open the dashboard and upload your file.</li>
        <li>Review the calculated statistics and charts. Rows in the table are coloured by CV%.</li>
        <li>Export your review as CSV or PDF when done.</li>
      </ol>
      <p>CV% helps indicate variation between devices. Altman-Bland plots show agreement against the target.</p>
    </div>
  );
}
