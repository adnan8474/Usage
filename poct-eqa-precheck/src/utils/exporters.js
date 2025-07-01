import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import Papa from 'papaparse';

export function exportCSV(rows) {
  const csv = Papa.unparse(rows);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'eqa_results.csv';
  link.click();
}

export async function exportPDF(rows, stats) {
  const doc = new jsPDF();
  doc.text('EQA Report', 10, 10);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, 10, 20);
  const table = document.querySelector('table');
  if (table) {
    const canvas = await html2canvas(table);
    const imgData = canvas.toDataURL('image/png');
    doc.addImage(imgData, 'PNG', 10, 30, 180, 60);
  }
  const charts = document.querySelectorAll('.chart-container');
  let y = 100;
  for (const el of charts) {
    const canvas = await html2canvas(el);
    const img = canvas.toDataURL('image/png');
    doc.addImage(img, 'PNG', 10, y, 180, 60);
    y += 70;
  }
  doc.save('eqa_report.pdf');
}
