import dayjs from 'dayjs';

/** Generate sample dataset with 20 rows and some anomalies */
export function generateSampleData() {
  const ops = ['OP001', 'OP002', 'OP003'];
  const devices = ['ABL90_01', 'ABL90_02'];
  const locations = ['ICU', 'Ward1'];
  const rows = [];
  let time = dayjs('2025-06-01T08:00:00');
  for (let i = 0; i < 20; i++) {
    rows.push({
      timestamp: time.add(i * 10, 'minute'),
      operator: ops[i % ops.length],
      device: devices[i % devices.length],
      location: locations[i % locations.length],
      test: 'Glucose',
    });
  }
  // Insert anomaly: same operator in two locations
  rows[5] = { ...rows[4], timestamp: rows[4].timestamp.add(5, 'minute'), device: 'ABL90_02', location: 'Ward1' };
  return rows;
}
