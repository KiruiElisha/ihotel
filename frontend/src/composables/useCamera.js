import { onBeforeUnmount, ref } from 'vue'

/**
 * Minimal camera helper for document capture.
 *
 * Wraps getUserMedia so a dialog can start/stop the rear camera, bind the
 * stream to a <video>, and grab a still frame as a JPEG data URL for storage
 * or client-side decoding. Every browser without camera access still works —
 * the caller falls back to manual entry.
 */
export function useCamera() {
  const stream = ref(null)
  const active = ref(false)
  const error = ref('')
  const videoEl = ref(null)

  async function start() {
    error.value = ''
    if (!navigator.mediaDevices?.getUserMedia) {
      error.value = 'Camera not available on this device.'
      return false
    }
    try {
      stream.value = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false,
      })
      active.value = true
      if (videoEl.value) {
        videoEl.value.srcObject = stream.value
        await videoEl.value.play().catch(() => {})
      }
      return true
    } catch (e) {
      error.value =
        e?.name === 'NotAllowedError'
          ? 'Camera permission denied.'
          : 'Could not start the camera.'
      return false
    }
  }

  function stop() {
    stream.value?.getTracks().forEach((t) => t.stop())
    stream.value = null
    active.value = false
    if (videoEl.value) videoEl.value.srcObject = null
  }

  /** Capture the current frame as a JPEG data URL (or '' if not ready). */
  function capture(maxWidth = 1280) {
    const video = videoEl.value
    if (!video || !video.videoWidth) return ''
    const scale = Math.min(1, maxWidth / video.videoWidth)
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(video.videoWidth * scale)
    canvas.height = Math.round(video.videoHeight * scale)
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg', 0.85)
  }

  onBeforeUnmount(stop)

  return { videoEl, stream, active, error, start, stop, capture }
}
