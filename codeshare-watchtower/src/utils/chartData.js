import groupBy from 'lodash.groupby';

/** Build datasets for operator timeline chart */
export function buildTimelineSeries(events) {
  const byOp = groupBy(events, e => e.operator);
  return Object.entries(byOp).map(([op, ops], idx) => ({
    label: op,
    data: ops.map(ev => ({ x: ev.timestamp.toDate(), y: idx })),
  }));
}

/** Aggregate hourly counts across all operators */
export function buildHourlyCounts(events) {
  const counts = Array.from({ length: 24 }, () => 0);
  events.forEach(e => {
    counts[e.timestamp.hour()]++;
  });
  return counts;
}

/** Build device-location usage matrix */
export function buildDeviceLocationMatrix(events) {
  const matrix = {};
  events.forEach(e => {
    if (!matrix[e.device]) matrix[e.device] = {};
    matrix[e.device][e.location] = (matrix[e.device][e.location] || 0) + 1;
  });
  return matrix;
}

/** Box plot stats for time-of-day usage */
export function buildBoxPlotData(events) {
  const byOp = groupBy(events, e => e.operator);
  const labels = [];
  const data = [];
  Object.entries(byOp).forEach(([op, ops]) => {
    const hours = ops.map(e => e.timestamp.hour()).sort((a, b) => a - b);
    const q1 = quantile(hours, 0.25);
    const median = quantile(hours, 0.5);
    const q3 = quantile(hours, 0.75);
    const min = hours[0];
    const max = hours[hours.length - 1];
    labels.push(op);
    data.push({ min, q1, median, q3, max });
  });
  return { labels, data };
}

function quantile(arr, q) {
  const pos = (arr.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (arr[base + 1] !== undefined) {
    return arr[base] + rest * (arr[base + 1] - arr[base]);
  }
  return arr[base];
}
