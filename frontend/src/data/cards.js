import { createResource } from 'frappe-ui'

/**
 * Card-integration data layer: ID/passport scanning and room-key encoding.
 * Thin wrappers over the ihotel.card_api whitelisted methods so pages and
 * dialogs share one definition of each call.
 */

/** Feature flags + provider/vendor config for rendering the scan/encode UI. */
export const cardSettings = createResource({
  url: 'ihotel.card_api.get_card_settings',
  cache: 'ihotel-card-settings',
  auto: true,
})

/** Parse a decoded MRZ / AAMVA payload into structured guest fields. */
export function scanId(rawText) {
  return createResource({ url: 'ihotel.card_api.scan_id' }).submit({ raw_text: rawText })
}

/** Write scanned fields onto a guest (creates one when `guest` is omitted). */
export function applyIdToGuest({ data, guest, frontImage, backImage }) {
  return createResource({ url: 'ihotel.card_api.apply_id_to_guest' }).submit({
    data: JSON.stringify(data),
    guest: guest || null,
    front_image: frontImage || null,
    back_image: backImage || null,
  })
}

/** Encode a room key and log a Key Card. */
export function encodeKey(params) {
  return createResource({ url: 'ihotel.card_api.encode_key' }).submit(params)
}

/** Cancel/invalidate a previously issued key. */
export function cancelKey(keyCard) {
  return createResource({ url: 'ihotel.card_api.cancel_key' }).submit({ key_card: keyCard })
}

/** List Key Cards for a stay / room / guest. */
export function listKeys(filters) {
  return createResource({ url: 'ihotel.card_api.list_keys' }).submit(filters)
}
