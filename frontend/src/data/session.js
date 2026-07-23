import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'

/** Who the current user is. Resolved server-side; the client never asserts a role. */
export const boot = createResource({
  url: 'ihotel.frontend_api.get_boot',
  cache: 'ihotel-boot',
})

export const session = reactive({
  get user() {
    return boot.data?.user
  },
  get fullName() {
    return boot.data?.full_name || boot.data?.user
  },
  get hotelName() {
    return boot.data?.hotel_name || 'iHotel'
  },
  get canManage() {
    return Boolean(boot.data?.can_manage)
  },
  get isLoggedIn() {
    return Boolean(boot.data?.user) && boot.data.user !== 'Guest'
  },
})

export const isReady = computed(() => Boolean(boot.data) || Boolean(boot.error))

let loading = null

export function ensureBoot() {
  if (boot.data) return Promise.resolve(boot.data)
  if (!loading) {
    loading = boot.fetch().finally(() => {
      loading = null
    })
  }
  return loading
}

export async function logout() {
  await fetch('/api/method/logout', { method: 'POST', credentials: 'include' })
  window.location.href = '/login'
}
