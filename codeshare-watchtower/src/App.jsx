import React, { useState } from 'react';
import { parseCSV } from './utils/dataProcessor.js';
import { detectCollisions, detectUnusualPatterns, detectDeviceWardViolations } from './utils/anomalyDetector.js';
import UploadArea from './components/UploadArea.jsx';
import SuspiciousTable from './components/SuspiciousTable.jsx';
import ExportPanel from './components/ExportPanel.jsx';
import SampleDataButton from './components/SampleDataButton.jsx';

function App() {
  const [events, setEvents] = useState([]);
  const [flags, setFlags] = useState([]);

  const handleData = async (csvText) => {
    const parsed = await parseCSV(csvText);
    setEvents(parsed);
    const collisions = detectCollisions(parsed);
    const unusual = detectUnusualPatterns(parsed);
    const ward = detectDeviceWardViolations(parsed);
    setFlags([...collisions, ...unusual, ...ward]);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">CodeShare Watchtower</h1>
      <UploadArea onData={handleData} />
      <div className="flex mb-2">
        <SampleDataButton onFlags={setFlags} />
      </div>
      <SuspiciousTable flags={flags} />
      <ExportPanel flags={flags} />
    </div>
  );
}

export default App;
