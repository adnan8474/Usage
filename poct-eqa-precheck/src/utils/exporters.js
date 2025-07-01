import { utils, writeFile } from 'xlsx';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export function exportCSV(rows) {
  const ws = utils.json_to_sheet(rows);
  const wb = utils.book_new();
  utils.book_append_sheet(wb, ws, 'Results');
  writeFile(wb, 'eqa_results.xlsx');
}

export async function exportPDF(rows, stats) {
  const doc = new jsPDF();
  doc.text('EQA Report', 10, 10);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, 10, 20);
  const table = document.querySelector('table');
  if (table) {
    const canvas = await html2canvas(table);
    const imgData = canvas.toDataURL('image/png');
    doc.addImage(imgData, 'PNG', 10, 30, 180, 100);
  }
  doc.save('eqa_report.pdf');
}
