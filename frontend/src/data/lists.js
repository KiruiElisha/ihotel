import { createResource } from 'frappe-ui'

/** Dropdown sources for the front-desk forms. Fetched once and shared. */
export const lists = createResource({
  url: 'ihotel.frontend_api.get_lists',
  cache: 'ihotel-lists',
  auto: true,
})
