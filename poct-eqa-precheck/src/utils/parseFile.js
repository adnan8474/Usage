import Papa from 'papaparse';
import * as XLSX from 'xlsx';

export async function parseFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  if (ext === 'csv') {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        complete: (results) => resolve(cleanRows(results.data)),
        error: reject,
      });
    });
  }
  if (ext === 'xlsx') {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type: 'array' });
    const ws = wb.Sheets[wb.SheetNames[0]];
    const json = XLSX.utils.sheet_to_json(ws);
    return cleanRows(json);
  }
  throw new Error('Unsupported file type');
}

function cleanRows(rows) {
  return rows
    .map(r => ({
      device_id: r.device_id || r.Device || r.device || '',
      analyte: r.analyte,
      test_date: r.test_date || r.date,
      measured_value: parseFloat(r.measured_value || r.measured || r.value),
      target_value: parseFloat(r.target_value || r.target),
    }))
    .filter(r => r.device_id && !isNaN(r.measured_value) && !isNaN(r.target_value));
}
