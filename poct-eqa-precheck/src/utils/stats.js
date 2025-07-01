export function groupByDevice(rows) {
  return rows.reduce((acc, row) => {
    if (!acc[row.device_id]) acc[row.device_id] = [];
    acc[row.device_id].push(row);
    return acc;
  }, {});
}

export function deviceStats(rows) {
  const values = rows.map(r => r.measured_value);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
  const sd = Math.sqrt(variance);
  const cv = (sd / mean) * 100;
  return { mean, sd, cv, count: values.length };
}

export function computeStats(rows) {
  if (!rows.length) return { devices: 0, mean: 0, sd: 0, cv: 0, analyte: '' };
  const grouped = groupByDevice(rows);
  const allValues = rows.map(r => r.measured_value);
  const mean = allValues.reduce((a, b) => a + b, 0) / allValues.length;
  const variance = allValues.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / allValues.length;
  const sd = Math.sqrt(variance);
  const cv = (sd / mean) * 100;
  return {
    devices: Object.keys(grouped).length,
    mean,
    sd,
    cv,
    analyte: rows[0].analyte,
  };
}
