<template>
  <PageHeader title="Room Board">
    <template #actions>
      <Button
        label="Refresh"
        :loading="board.loading"
        :icon-left="LucideRefreshCw"
        @click="board.reload()"
      />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="select" size="sm" v-model="filters.status" :options="statusChoices" />
    <FormControl type="select" size="sm" v-model="filters.floor" :options="floorChoices" />
    <FormControl type="text" size="sm" placeholder="Room or guest" v-model="search" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rooms.length }} rooms</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="board.error" />

    <!-- A board, not a table: at a glance you want colour and room number. -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6">
      <button
        v-for="room in rooms"
        :key="room.name"
        type="button"
        class="rounded-lg border p-3 text-left transition-colors hover:border-outline-gray-3"
        :class="tone(room.status)"
        @click="open(room)"
      >
        <div class="flex items-start justify-between gap-2">
          <span class="text-lg font-semibold tabular-nums">{{ room.room_number }}</span>
          <Badge :theme="badgeTheme(room.status)">{{ room.status || '—' }}</Badge>
        </div>
        <p class="mt-1 truncate text-xs opacity-80">{{ room.room_type || 'No type' }}</p>
        <p class="mt-2 truncate text-sm font-medium">
          {{ room.guest || 'Vacant' }}
        </p>
        <p v-if="room.due_out" class="mt-0.5 text-xs opacity-80">
          Due out {{ date(room.due_out) }}
        </p>
      </button>
    </div>

    <p v-if="!rooms.length" class="rounded-lg border border-outline-gray-1 p-8 text-center text-ink-gray-6">
      No rooms match these filters.
    </p>
  </div>

  <Dialog v-model="showRoom" :options="{ title: selected.room_number ? `Room ${selected.room_number}` : 'Room' }">
    <template #body-content>
      <dl class="space-y-3 text-sm">
        <div class="flex justify-between gap-4">
          <dt class="text-ink-gray-5">Type</dt>
          <dd class="font-medium text-ink-gray-9">{{ selected.room_type || '—' }}</dd>
        </div>
        <div class="flex justify-between gap-4">
          <dt class="text-ink-gray-5">Floor</dt>
          <dd class="font-medium text-ink-gray-9">{{ selected.floor || '—' }}</dd>
        </div>
        <div class="flex justify-between gap-4">
          <dt class="text-ink-gray-5">Guest</dt>
          <dd class="font-medium text-ink-gray-9">{{ selected.guest || 'Vacant' }}</dd>
        </div>
        <div v-if="selected.checked_in_on" class="flex justify-between gap-4">
          <dt class="text-ink-gray-5">Checked in</dt>
          <dd class="font-medium text-ink-gray-9">{{ date(selected.checked_in_on) }}</dd>
        </div>
      </dl>

      <FormControl
        class="mt-5"
        type="select"
        label="Room status"
        v-model="nextStatus"
        :options="statusOptions"
      />
      <ErrorMessage class="mt-3" :message="updateStatus.error" />
    </template>
    <template #actions>
      <Button
        class="w-full"
        variant="solid"
        theme="blue"
        label="Update status"
        :loading="updateStatus.loading"
        :disabled="!nextStatus || nextStatus === selected.status"
        @click="updateStatus.submit({ room: selected.name, status: nextStatus })"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Badge, Button, Dialog, ErrorMessage, FormControl, createResource, toast } from 'frappe-ui'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import PageHeader from '@/components/PageHeader.vue'
import { date } from '@/data/format'

const board = createResource({
  url: 'ihotel.frontend_api.get_room_board',
  auto: true,
})

const filters = reactive({ status: '', floor: '' })
const search = ref('')

const statusChoices = computed(() => [
  { label: 'All statuses', value: '' },
  ...(board.data?.statuses || []).map((s) => ({ label: s, value: s })),
])
const floorChoices = computed(() => [
  { label: 'All floors', value: '' },
  ...(board.data?.floors || []).map((f) => ({ label: `Floor ${f}`, value: f })),
])
const statusOptions = computed(() =>
  (board.data?.statuses || []).map((s) => ({ label: s, value: s })),
)

const rooms = computed(() => {
  const q = search.value.trim().toLowerCase()
  return (board.data?.rooms || []).filter((room) => {
    if (filters.status && room.status !== filters.status) return false
    if (filters.floor && String(room.floor) !== String(filters.floor)) return false
    if (!q) return true
    return (
      String(room.room_number || '').toLowerCase().includes(q) ||
      String(room.guest || '').toLowerCase().includes(q)
    )
  })
})

// Colour carries the status at a glance; the badge repeats it in words so the
// board is not colour-only.
// Room.status has twelve values; group them so the board reads at a glance.
const clean = ['Available', 'Vacant Clean', 'Inspected']
const dirty = ['Dirty', 'Vacant Dirty', 'Occupied Dirty', 'Pickup', 'Housekeeping']
const outOfUse = ['Out of Order', 'Out of Service']

const group = (status) => {
  if (clean.includes(status)) return 'clean'
  if (dirty.includes(status)) return 'dirty'
  if (outOfUse.includes(status)) return 'out'
  if (status) return 'occupied'
  return 'unknown'
}

const tone = (status) =>
  ({
    clean: 'border-green-200 bg-green-50 text-green-900',
    occupied: 'border-navy-200 bg-navy-50 text-navy-900',
    dirty: 'border-brass-200 bg-brass-50 text-brass-600',
    out: 'border-red-200 bg-red-50 text-red-900',
  })[group(status)] || 'border-outline-gray-2 bg-surface-white text-ink-gray-8'

const badgeTheme = (status) =>
  ({ clean: 'green', occupied: 'blue', dirty: 'orange', out: 'red' })[group(status)] || 'gray'

const showRoom = ref(false)
const selected = ref({})
const nextStatus = ref('')

function open(room) {
  selected.value = room
  nextStatus.value = room.status || ''
  showRoom.value = true
}

const updateStatus = createResource({
  url: 'ihotel.frontend_api.set_room_status',
  onSuccess: () => {
    showRoom.value = false
    toast.success('Room status updated')
    board.reload()
  },
})
</script>
