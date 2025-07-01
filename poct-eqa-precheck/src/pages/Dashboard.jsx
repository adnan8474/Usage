import React, { useState } from 'react';
import UploadArea from '../components/UploadArea.jsx';
import SummaryPanel from '../components/SummaryPanel.jsx';
import ChartsPanel from '../components/ChartsPanel.jsx';
import StatsTable from '../components/StatsTable.jsx';
import ExportPanel from '../components/ExportPanel.jsx';
import { parseFile } from '../utils/parseFile.js';
import { computeStats } from '../utils/stats.js';

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [stats, setStats] = useState({ devices: 0, mean: 0, sd: 0, cv: 0, analyte: '' });

  const handleFile = async (file) => {
    const rows = await parseFile(file);
    setData(rows);
    setStats(computeStats(rows));
  };

  return (
    <div className="space-y-6">
      <UploadArea onFile={handleFile} />
      {data.length > 0 && (
        <>
          <SummaryPanel stats={stats} />
          <ChartsPanel data={data} />
          <StatsTable data={data} />
          <ExportPanel data={data} stats={stats} />
        </>
      )}
    </div>
  );
}
