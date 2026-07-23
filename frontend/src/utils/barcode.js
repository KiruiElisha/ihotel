/**
 * Best-effort client-side decode of the PDF417 barcode on the back of a
 * driver license. Uses @zxing/library, dynamically imported so the app still
 * builds and the manual-entry path still works if the dependency is absent.
 *
 * Returns the decoded text, or throws so the caller can fall back to manual
 * entry.
 */
export async function decodePdf417FromImage(dataUrl) {
  let zxing
  try {
    zxing = await import('@zxing/library')
  } catch (e) {
    throw new Error('Barcode decoder is not installed; enter the code manually.')
  }
  const { MultiFormatReader, BarcodeFormat, DecodeHintType, RGBLuminanceSource, BinaryBitmap, HybridBinarizer } =
    zxing

  const img = await loadImage(dataUrl)
  const canvas = document.createElement('canvas')
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0)
  const { data, width, height } = ctx.getImageData(0, 0, canvas.width, canvas.height)

  // Pack RGBA into the luminance source ZXing expects.
  const luminances = new Uint8ClampedArray(width * height)
  for (let i = 0, j = 0; i < data.length; i += 4, j++) {
    luminances[j] = (data[i] * 3 + data[i + 1] * 4 + data[i + 2]) >> 3
  }
  const source = new RGBLuminanceSource(luminances, width, height)
  const bitmap = new BinaryBitmap(new HybridBinarizer(source))

  const hints = new Map()
  hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.PDF_417])
  hints.set(DecodeHintType.TRY_HARDER, true)

  const reader = new MultiFormatReader()
  reader.setHints(hints)
  const result = reader.decode(bitmap, hints)
  return result.getText()
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('Could not load captured image.'))
    img.src = src
  })
}
