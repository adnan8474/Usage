import dayjs from 'dayjs';
import groupBy from 'lodash.groupby';

/**
 * Detect temporal & spatial collisions where the same operator is
 * seen at different devices or locations within a 15 minute window.
 */
export function detectCollisions(events, windowMinutes = 15) {
  const flagged = [];
  const byOperator = groupBy(events, e => e.operator);
  Object.entries(byOperator).forEach(([op, ops]) => {
    ops.sort((a, b) => a.timestamp - b.timestamp);
    for (let i = 0; i < ops.length - 1; i++) {
      const current = ops[i];
      for (let j = i + 1; j < ops.length; j++) {
        const compare = ops[j];
        if (compare.timestamp.diff(current.timestamp, 'minute') > windowMinutes) break;
        if (current.device !== compare.device || current.location !== compare.location) {
          flagged.push({ operator: op, current, compare });
        }
      }
    }
  });
  return flagged;
}

/**
 * Build operator usage profiles and detect activities outside ±2 std devs.
 */
export function detectUnusualPatterns(events) {
  const byOperator = groupBy(events, e => e.operator);
  const flagged = [];
  Object.entries(byOperator).forEach(([op, ops]) => {
    const hours = ops.map(e => e.timestamp.hour());
    const mean = hours.reduce((a, b) => a + b, 0) / hours.length;
    const variance = hours.reduce((a, b) => a + (b - mean) ** 2, 0) / hours.length;
    const std = Math.sqrt(variance);
    ops.forEach(evt => {
      const h = evt.timestamp.hour();
      if (Math.abs(h - mean) > 2 * std) {
        flagged.push({ operator: op, event: evt, mean, std });
      }
    });
  });
  return flagged;
}

/**
 * Map devices to common locations and flag rare pairings.
 */
export function detectDeviceWardViolations(events, threshold = 0.1) {
  const deviceLocationCounts = {};
  events.forEach(e => {
    const key = `${e.device}|${e.location}`;
    deviceLocationCounts[key] = (deviceLocationCounts[key] || 0) + 1;
  });
  const deviceTotals = {};
  events.forEach(e => {
    deviceTotals[e.device] = (deviceTotals[e.device] || 0) + 1;
  });
  const rarePairs = new Set();
  Object.keys(deviceLocationCounts).forEach(key => {
    const [device, location] = key.split('|');
    const freq = deviceLocationCounts[key] / deviceTotals[device];
    if (freq < threshold) {
      rarePairs.add(key);
    }
  });
  return events.filter(e => rarePairs.has(`${e.device}|${e.location}`));
}
