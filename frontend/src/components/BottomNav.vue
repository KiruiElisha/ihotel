<template>
  <nav
    class="print-hide flex shrink-0 items-stretch border-t border-outline-gray-1 bg-surface-white pb-[env(safe-area-inset-bottom)] md:hidden"
    aria-label="Primary"
  >
    <button
      v-for="tab in tabs"
      :key="tab.label"
      type="button"
      class="flex h-14 flex-1 flex-col items-center justify-center gap-0.5 text-[11px] font-medium transition-colors"
      :class="isActive(tab) ? 'text-navy-500' : 'text-ink-gray-5'"
      :aria-current="isActive(tab) ? 'page' : undefined"
      @click="onTab(tab)"
    >
      <component :is="tab.icon" class="size-5" />
      <span>{{ tab.label }}</span>
    </button>
  </nav>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import LucideLayoutDashboard from '~icons/lucide/layout-dashboard'
import LucideBedDouble from '~icons/lucide/bed-double'
import LucideCalendarCheck from '~icons/lucide/calendar-check'
import LucideDoorOpen from '~icons/lucide/door-open'
import LucideMenu from '~icons/lucide/menu'
import { haptic } from '@/utils/haptics'

const emit = defineEmits(['more'])
const route = useRoute()
const router = useRouter()

// The four a front-desk uses all day; everything else sits behind More.
const tabs = [
  { name: 'Dashboard', label: 'Today', icon: LucideLayoutDashboard },
  { name: 'RoomBoard', label: 'Rooms', icon: LucideBedDouble },
  { name: 'Reservations', label: 'Bookings', icon: LucideCalendarCheck },
  { name: 'InHouse', label: 'In House', icon: LucideDoorOpen },
  { label: 'More', icon: LucideMenu, more: true },
]

const isActive = (tab) => !tab.more && route.name === tab.name

function onTab(tab) {
  haptic()
  if (tab.more) return emit('more')
  if (!isActive(tab)) router.push({ name: tab.name })
}
</script>
