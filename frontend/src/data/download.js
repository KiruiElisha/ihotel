/** Client-side CSV export. Keeps statements downloadable without a server round trip. */

function escapeCell(value) {
  const text = value === null || value === undefined ? '' : String(value)
  // Quote anything containing a delimiter, quote or newline; double inner quotes.
  return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text
}

export function toCsv(columns, rows) {
  const header = columns.map((c) => escapeCell(c.label)).join(',')
  const body = rows.map((row) =>
    columns.map((c) => escapeCell(c.value(row))).join(','),
  )
  return [header, ...body].join('\r\n')
}

export function downloadCsv(filename, columns, rows) {
  // The BOM makes Excel open UTF-8 correctly instead of mangling accents.
  const blob = new Blob(['﻿' + toCsv(columns, rows)], {
    type: 'text/csv;charset=utf-8;',
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/** Date stamp for filenames: 2026-07-23. */
export function stamp() {
  return new Date().toISOString().slice(0, 10)
}
