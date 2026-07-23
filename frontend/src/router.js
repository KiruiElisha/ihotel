import { createRouter, createWebHistory } from 'vue-router'
import { ensureBoot, session } from './data/session'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
  { path: '/rooms', name: 'RoomBoard', component: () => import('@/pages/RoomBoard.vue') },
  { path: '/reservations', name: 'Reservations', component: () => import('@/pages/Reservations.vue') },
  { path: '/guests', name: 'Guests', component: () => import('@/pages/Guests.vue') },
  { path: '/in-house', name: 'InHouse', component: () => import('@/pages/InHouse.vue') },
  { path: '/housekeeping', name: 'Housekeeping', component: () => import('@/pages/Housekeeping.vue') },
  { path: '/maintenance', name: 'Maintenance', component: () => import('@/pages/Maintenance.vue') },
  { path: '/laundry', name: 'Laundry', component: () => import('@/pages/Laundry.vue') },
  { path: '/night-audit', name: 'NightAudit', component: () => import('@/pages/NightAudit.vue') },
  { path: '/no-access', name: 'NoAccess', component: () => import('@/pages/NoAccess.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory('/hotel'),
  routes,
})

router.beforeEach(async (to) => {
  await ensureBoot()

  if (!session.isLoggedIn) {
    window.location.href = `/login?redirect-to=/hotel${to.fullPath}`
    return false
  }

  if (to.name === 'NoAccess') return true
  if (!session.canManage) return { name: 'NoAccess' }

  return true
})

export default router
