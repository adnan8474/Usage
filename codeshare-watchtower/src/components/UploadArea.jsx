import React from 'react';
import { validateHeaders } from '../utils/validators.js';

/** Drag & drop CSV area */
function UploadArea({ onData }) {
  const handleFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const text = await file.text();
    const firstLine = text.split(/\r?\n/)[0];
    const headers = firstLine.split(',');
    try {
      validateHeaders(headers);
    } catch (err) {
      alert(err.message);
      return;
    }
    onData(text);
  };

  return (
    <div className="border-dashed border-2 p-4 mb-4 rounded">
      <input type="file" accept=".csv" onChange={handleFile} />
    </div>
  );
}

export default UploadArea;
