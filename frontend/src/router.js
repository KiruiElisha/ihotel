import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/reservations',
    name: 'Reservations',
    component: () => import('@/pages/Reservations.vue'),
  },
  {
    path: '/room-board',
    name: 'RoomBoard',
    component: () => import('@/pages/RoomBoard.vue'),
  },
  {
    path: '/guests',
    name: 'Guests',
    component: () => import('@/pages/Guests.vue'),
  },
  {
    path: '/housekeeping',
    name: 'Housekeeping',
    component: () => import('@/pages/Housekeeping.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

export default router
