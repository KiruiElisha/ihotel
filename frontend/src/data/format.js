const KES = new Intl.NumberFormat('en-KE', {
  style: 'currency',
  currency: 'KES',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
})

export function currency(value, { compact = false } = {}) {
  const n = Number(value) || 0
  if (compact && Math.abs(n) >= 1000) {
    return `KSh ${new Intl.NumberFormat('en-KE', {
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(n)}`
  }
  return KES.format(n)
}

export function number(value, decimals = 0) {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(Number(value) || 0)
}

export function percent(value, decimals = 2) {
  return `${number(value, decimals)}%`
}

export function date(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

/** Today as yyyy-mm-dd, for date field defaults. */
export function today() {
  return new Date().toISOString().slice(0, 10)
}

/** yyyy-mm-dd `days` from today. */
export function daysFromToday(days) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

/** A short date-time for activity feeds: 23 Jul, 14:05. */
export function dateTime(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** How long ago, in plain words. */
export function timeAgo(value) {
  if (!value) return ''
  const then = new Date(value).getTime()
  if (Number.isNaN(then)) return ''
  const mins = Math.round((Date.now() - then) / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.round(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.round(hours / 24)}d ago`
}

/** Nights between two dates. */
export function nights(from, to) {
  if (!from || !to) return 0
  const a = new Date(from).getTime()
  const b = new Date(to).getTime()
  if (Number.isNaN(a) || Number.isNaN(b)) return 0
  return Math.max(0, Math.round((b - a) / 86400000))
}
