/** Lightweight tap haptic (Android Chrome and similar). A no-op elsewhere. */
export function haptic(ms = 8) {
  try {
    if (typeof navigator !== 'undefined' && navigator.vibrate) navigator.vibrate(ms)
  } catch {
    /* vibration is a nicety; never let it break a tap */
  }
}
