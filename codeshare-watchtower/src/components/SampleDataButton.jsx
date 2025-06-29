import React from 'react';
import { generateSampleData } from '../utils/sampleData.js';
import { detectCollisions, detectUnusualPatterns, detectDeviceWardViolations } from '../utils/anomalyDetector.js';

function SampleDataButton({ onData, onFlags }) {
  const loadSample = () => {
    const data = generateSampleData();
    const collisions = detectCollisions(data);
    const unusual = detectUnusualPatterns(data);
    const ward = detectDeviceWardViolations(data);
    onFlags([...collisions, ...unusual, ...ward]);
    onData(data);
  };

  return (
    <button onClick={loadSample} className="px-3 py-2 bg-green-500 text-white rounded mr-2">
      Load Sample
    </button>
  );
}

export default SampleDataButton;
