import Papa from 'papaparse';
import dayjs from 'dayjs';

/**
 * Parse a CSV string into structured event objects.
 * Expected columns: Timestamp,Operator ID,Device,Location,Test Type
 */
export function parseCSV(text) {
  return new Promise((resolve, reject) => {
    Papa.parse(text, {
      header: true,
      skipEmptyLines: true,
      complete: results => {
        const data = results.data.map(row => ({
          timestamp: dayjs(row['Timestamp']),
          operator: row['Operator ID'],
          device: row['Device'],
          location: row['Location'],
          test: row['Test Type'],
        }));
        resolve(data);
      },
      error: reject,
    });
  });
}
