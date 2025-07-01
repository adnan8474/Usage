import React, { useRef } from 'react';

export default function UploadArea({ onFile }) {
  const inputRef = useRef();

  const handleFiles = (files) => {
    if (files.length) {
      onFile(files[0]);
    }
  };

  return (
    <div className="border-2 border-dashed p-6 text-center rounded">
      <input
        type="file"
        accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
        className="hidden"
        ref={inputRef}
        onChange={(e) => handleFiles(e.target.files)}
      />
      <p className="mb-2">Drag and drop or select a CSV/XLSX file</p>
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded"
        onClick={() => inputRef.current.click()}
      >
        Select File
      </button>
      <a href="/template.csv" className="ml-4 text-blue-600 underline">
        Download Template
      </a>
    </div>
  );
}
