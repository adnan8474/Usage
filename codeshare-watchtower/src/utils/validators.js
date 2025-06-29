/** Validate CSV headers */
export function validateHeaders(headers) {
  const required = ['Timestamp','Operator ID','Device','Location','Test Type'];
  const missing = required.filter(h => !headers.includes(h));
  if (missing.length) {
    throw new Error(`Missing columns: ${missing.join(', ')}`);
  }
}
