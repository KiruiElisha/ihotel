/**
 * One place that decides what colour a status means.
 *
 * The app shows statuses from a dozen doctypes (rooms, reservations, stays,
 * housekeeping, maintenance, key cards, payments). Mapping them here keeps the
 * meaning consistent everywhere: green reads "ready/done", orange "needs
 * attention", red "blocked/problem", blue "in progress", grey "inactive".
 */

// frappe-ui Badge themes.
const GREEN = 'green'
const ORANGE = 'orange'
const RED = 'red'
const BLUE = 'blue'
const GRAY = 'gray'

const THEMES = {
  // --- Room ---
  available: GREEN,
  'vacant clean': GREEN,
  inspected: GREEN,
  occupied: BLUE,
  'occupied clean': BLUE,
  dirty: ORANGE,
  'vacant dirty': ORANGE,
  'occupied dirty': ORANGE,
  pickup: ORANGE,
  housekeeping: ORANGE,
  'out of order': RED,
  'out of service': RED,

  // --- Reservation (stored lower-case) ---
  pending: ORANGE,
  confirmed: GREEN,
  checked_in: BLUE,
  cancelled: GRAY,

  // --- Checked In ---
  reserved: ORANGE,
  'checked in': GREEN,
  'checked out': GRAY,
  'no show': RED,

  // --- Housekeeping / Maintenance ---
  'in progress': BLUE,
  completed: GREEN,
  open: RED,
  resolved: GREEN,
  closed: GRAY,

  // --- Priority ---
  low: GRAY,
  normal: BLUE,
  medium: BLUE,
  high: ORANGE,
  urgent: RED,
  critical: RED,

  // --- Key Card ---
  encoded: GREEN,
  active: GREEN,
  expired: ORANGE,
  failed: RED,

  // --- In-house "Due" column (derived, not stored) ---
  staying: GREEN,
  'due out': ORANGE,

  // --- Payment ---
  paid: GREEN,
  unpaid: RED,
  partial: ORANGE,
  overdue: RED,
  refunded: GRAY,
}

/** Badge theme for a status value. Falls back to grey for anything unmapped. */
export function statusTheme(value) {
  if (!value) return GRAY
  return THEMES[String(value).toLowerCase().trim()] || GRAY
}

// Light background + readable text, for row tints and pill chips. Deliberately
// the 50/100 end of each ramp so a whole list of them stays calm.
const TINTS = {
  green: 'bg-green-50 text-green-800 ring-green-200',
  orange: 'bg-orange-50 text-orange-800 ring-orange-200',
  red: 'bg-red-50 text-red-800 ring-red-200',
  blue: 'bg-navy-50 text-navy-900 ring-navy-200',
  gray: 'bg-surface-gray-2 text-ink-gray-7 ring-outline-gray-2',
}

/** Light tint classes for a status value (chips, row accents). */
export function statusTint(value) {
  return TINTS[statusTheme(value)] || TINTS.gray
}

/** Just the left-border accent colour, for list rows. */
const ACCENTS = {
  green: 'border-l-green-400',
  orange: 'border-l-orange-400',
  red: 'border-l-red-400',
  blue: 'border-l-navy-400',
  gray: 'border-l-outline-gray-3',
}

export function statusAccent(value) {
  return ACCENTS[statusTheme(value)] || ACCENTS.gray
}

/** Turn a stored value like "checked_in" into "Checked In" for display. */
export function statusLabel(value) {
  if (!value) return '—'
  return String(value)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
