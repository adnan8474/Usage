import React, { useState } from 'react';
import { parseCSV } from './utils/dataProcessor.js';
import {
  detectCollisions,
  detectUnusualPatterns,
  detectDeviceWardViolations,
} from './utils/anomalyDetector.js';
import UploadArea from './components/UploadArea.jsx';
import SuspiciousTable from './components/SuspiciousTable.jsx';
import ExportPanel from './components/ExportPanel.jsx';
import SampleDataButton from './components/SampleDataButton.jsx';
import TimelineChart from './components/TimelineChart.jsx';
import Heatmap from './components/Heatmap.jsx';
import DeviceMap from './components/DeviceMap.jsx';
import BoxPlotChart from './components/BoxPlot.jsx';

function App() {
  const [events, setEvents] = useState([]);
  const [flags, setFlags] = useState([]);
  const [dark, setDark] = useState(false);

  const handleData = async (csvText) => {
    const parsed = await parseCSV(csvText);
    setEvents(parsed);
    const collisions = detectCollisions(parsed);
    const unusual = detectUnusualPatterns(parsed);
    const ward = detectDeviceWardViolations(parsed);
    setFlags([...collisions, ...unusual, ...ward]);
  };

  return (
    <div className={`container mx-auto p-4 ${dark ? 'dark' : ''}`}>
      <h1 className="text-2xl font-bold mb-4">CodeShare Watchtower</h1>
      <button
        onClick={() => setDark(!dark)}
        className="mb-2 px-2 py-1 border rounded"
      >
        Toggle Theme
      </button>
      <UploadArea onData={handleData} />
      <div className="flex mb-2">
        <SampleDataButton onData={setEvents} onFlags={setFlags} />
      </div>
      <SuspiciousTable flags={flags} />
      <TimelineChart events={events} />
      <DeviceMap events={events} />
      <BoxPlotChart events={events} />
      <Heatmap events={events} />
      <ExportPanel flags={flags} />
    </div>
  );
}

export default App;
