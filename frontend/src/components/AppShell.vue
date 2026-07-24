<template>
  <div
    class="flex h-full w-full overflow-hidden bg-surface-white"
    @touchstart.passive="onTouchStart"
    @touchmove.passive="onTouchMove"
  >
    <!-- Backdrop for the mobile drawer -->
    <div v-if="drawer" class="fixed inset-0 z-30 bg-black/40 md:hidden" @click="drawer = false" />

    <!-- Static on desktop; an off-canvas drawer on mobile. -->
    <div
      class="print-hide fixed left-0 top-0 z-40 h-full shadow-2xl transition-transform duration-200 ease-in-out md:static md:z-auto md:translate-x-0 md:shadow-none"
      :class="drawer ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <Sidebar :header="header" :sections="sections" :disable-collapse="isMobile">
        <template #header-logo>
          <img :src="logo" alt="" class="size-7 rounded" />
        </template>
        <template #footer-items="{ isCollapsed }">
          <ThemeSwitch>
            <template #default="{ current }">
              <SidebarItem :label="`Theme: ${current}`" :isCollapsed="isCollapsed">
                <template #icon>
                  <LucidePalette class="size-4 text-ink-gray-6" />
                </template>
              </SidebarItem>
            </template>
          </ThemeSwitch>
          <SidebarItem label="Open desk" :isCollapsed="isCollapsed" @click="goToDesk">
            <template #icon>
              <LucideExternalLink class="size-4 text-ink-gray-6" />
            </template>
          </SidebarItem>
          <SidebarItem label="Log out" :isCollapsed="isCollapsed" @click="logout">
            <template #icon>
              <LucideLogOut class="size-4 text-ink-gray-6" />
            </template>
          </SidebarItem>
        </template>
      </Sidebar>
    </div>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <main class="flex min-h-0 flex-1 flex-col overflow-hidden">
        <slot />
      </main>
      <BottomNav @more="openDrawer" />
    </div>
  </div>
</template>

<script setup>
import { computed, provide, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Sidebar, SidebarItem } from 'frappe-ui'
import BottomNav from '@/components/BottomNav.vue'
import ThemeSwitch from '@/components/ThemeSwitch.vue'
import { useIsMobile } from '@/composables/useIsMobile'
import { haptic } from '@/utils/haptics'
import { logout, session } from '@/data/session'

import LucideLayoutDashboard from '~icons/lucide/layout-dashboard'
import LucideBedDouble from '~icons/lucide/bed-double'
import LucideCalendarCheck from '~icons/lucide/calendar-check'
import LucideUsers from '~icons/lucide/users'
import LucideSparkles from '~icons/lucide/sparkles'
import LucideDoorOpen from '~icons/lucide/door-open'
import LucideWrench from '~icons/lucide/wrench'
import LucideShirt from '~icons/lucide/shirt'
import LucideMoonStar from '~icons/lucide/moon-star'
import LucideKeyRound from '~icons/lucide/key-round'
import LucideFileBarChart from '~icons/lucide/file-bar-chart'
import LucideLogOut from '~icons/lucide/log-out'
import LucideExternalLink from '~icons/lucide/external-link'
import LucidePalette from '~icons/lucide/palette'
import logo from '@/assets/logo.png'

const route = useRoute()

const goToDesk = () => (window.location.href = '/app/ihotel')

const isMobile = useIsMobile()
const drawer = ref(false)
watch(
  () => route.fullPath,
  () => (drawer.value = false),
)

function openDrawer() {
  haptic()
  drawer.value = true
}

// Page headers render inside the slot, so they reach the drawer through inject.
provide('openDrawer', openDrawer)

// Edge-swipe to open the drawer, swipe back to close it.
let startX = 0
let startY = 0
let fromEdge = false

function onTouchStart(e) {
  const t = e.touches[0]
  startX = t.clientX
  startY = t.clientY
  fromEdge = t.clientX < 24
}

function onTouchMove(e) {
  const t = e.touches[0]
  const dx = t.clientX - startX
  // Ignore mostly-vertical movement so this never fights page scrolling.
  if (Math.abs(t.clientY - startY) > 45) return
  if (!drawer.value && fromEdge && dx > 55) openDrawer()
  else if (drawer.value && dx < -55) drawer.value = false
}

const header = computed(() => ({
  title: session.hotelName,
  subtitle: session.fullName,
}))

const frontDeskItems = [
  { label: 'Today', icon: LucideLayoutDashboard, to: { name: 'Dashboard' } },
  { label: 'Room Board', icon: LucideBedDouble, to: { name: 'RoomBoard' } },
  { label: 'Reservations', icon: LucideCalendarCheck, to: { name: 'Reservations' } },
  { label: 'In House', icon: LucideDoorOpen, to: { name: 'InHouse' } },
  { label: 'Guests', icon: LucideUsers, to: { name: 'Guests' } },
]

const operationsItems = [
  { label: 'Housekeeping', icon: LucideSparkles, to: { name: 'Housekeeping' } },
  { label: 'Maintenance', icon: LucideWrench, to: { name: 'Maintenance' } },
  { label: 'Laundry', icon: LucideShirt, to: { name: 'Laundry' } },
  { label: 'Key Cards', icon: LucideKeyRound, to: { name: 'KeyCards' } },
]

const reportingItems = [
  { label: 'Reports', icon: LucideFileBarChart, to: { name: 'Reports' } },
  { label: 'Night Audit', icon: LucideMoonStar, to: { name: 'NightAudit' } },
]

const withActive = (items) =>
  items.map((item) => ({ ...item, isActive: route.name === item.to.name }))

const sections = computed(() => [
  { label: 'Front Desk', items: withActive(frontDeskItems) },
  { label: 'Operations', items: withActive(operationsItems) },
  { label: 'Reporting', items: withActive(reportingItems) },
])
</script>
