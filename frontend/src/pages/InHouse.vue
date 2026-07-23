<template>
  <PageHeader title="In House">
    <template #actions>
      <Button
        label="Refresh"
        :loading="inHouse.loading"
        :icon-left="LucideRefreshCw"
        @click="inHouse.reload()"
      />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="select" size="sm" v-model="view" :options="viewOptions" />
    <FormControl type="text" size="sm" placeholder="Guest or room" v-model="search" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rows.length }} stays</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="inHouse.error" />

    <div class="mb-5 grid grid-cols-2 gap-3 md:grid-cols-4">
      <StatTile label="In House" :value="totals.in_house ?? 0" hint="Occupied stays" />
      <StatTile label="Due Out Today" :value="totals.due_out ?? 0" />
      <StatTile
        label="Overdue"
        :value="totals.overdue ?? 0"
        hint="Past expected checkout"
      />
      <StatTile label="Room Revenue" :value="currency(totals.revenue)" hint="Open stays" />
    </div>

    <ResponsiveList
      :columns="columns"
      :rows="rows"
      :on-row-click="open"
      :empty-state="{ title: 'Nobody in house', description: 'Check a guest in to see them here.' }"
    >
      <template #card="{ row }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-ink-gray-9">{{ row.guest_name }}</p>
            <p class="mt-0.5 text-sm text-ink-gray-5">
              Room {{ row.room_number }} &middot; {{ row.room_type || '—' }}
            </p>
          </div>
          <Badge :theme="dueTheme(row)">{{ dueLabel(row) }}</Badge>
        </div>
        <dl class="mt-3 grid grid-cols-3 gap-2 border-t border-outline-gray-1 pt-3 text-sm">
          <div>
            <dt class="text-ink-gray-5">In</dt>
            <dd class="text-ink-gray-8">{{ date(row.actual_check_in) }}</dd>
          </div>
          <div>
            <dt class="text-ink-gray-5">Due out</dt>
            <dd class="text-ink-gray-8">{{ date(row.expected_check_out) }}</dd>
          </div>
          <div>
            <dt class="text-ink-gray-5">Amount</dt>
            <dd class="tabular-nums text-ink-gray-8">{{ currency(row.total_amount) }}</dd>
          </div>
        </dl>
      </template>
    </ResponsiveList>
  </div>

  <Dialog v-model="showStay" :options="{ title: selected.guest_name || 'Stay' }">
    <template #body-content>
      <dl class="space-y-3 text-sm">
        <div v-for="row in detail" :key="row.label" class="flex justify-between gap-4">
          <dt class="text-ink-gray-5">{{ row.label }}</dt>
          <dd class="text-right font-medium text-ink-gray-9">{{ row.value }}</dd>
        </div>
      </dl>
      <ErrorMessage class="mt-3" :message="checkOut.error" />
      <p class="mt-4 text-sm text-ink-gray-6">
        Checking out closes the stay and marks the room vacant dirty for housekeeping.
      </p>
    </template>
    <template #actions>
      <div class="flex gap-2">
        <Button
          v-if="keyEncodingEnabled"
          :icon-left="LucideKeyRound"
          label="Room keys"
          @click="showKeys = true"
        />
        <Button
          class="flex-1"
          variant="solid"
          theme="blue"
          label="Check out"
          :loading="checkOut.loading"
          @click="checkOut.submit({ stay: selected.name })"
        />
      </div>
    </template>
  </Dialog>

  <KeyCardDialog
    v-model="showKeys"
    :room="selected.room"
    :room-label="selected.room_number"
    :guest="selected.guest"
    :checked-in="selected.name"
    :valid-from="selected.actual_check_in"
    :valid-to="selected.expected_check_out"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import { Badge, Button, Dialog, ErrorMessage, FormControl, createResource, toast } from 'frappe-ui'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideKeyRound from '~icons/lucide/key-round'
import PageHeader from '@/components/PageHeader.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import StatTile from '@/components/StatTile.vue'
import KeyCardDialog from '@/components/KeyCardDialog.vue'
import { currency, date } from '@/data/format'
import { cardSettings } from '@/data/cards'

const inHouse = createResource({
  url: 'ihotel.frontend_api.get_in_house',
  auto: true,
})

const view = ref('')
const search = ref('')

const viewOptions = [
  { label: 'All stays', value: '' },
  { label: 'Due out today', value: 'due' },
  { label: 'Overdue', value: 'overdue' },
]

const totals = computed(() => inHouse.data?.totals || {})

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  return (inHouse.data?.stays || []).filter((row) => {
    if (view.value === 'due' && !row.due_out_today) return false
    if (view.value === 'overdue' && !row.overdue) return false
    if (!q) return true
    return [row.guest_name, row.room_number].some((v) =>
      String(v || '').toLowerCase().includes(q),
    )
  })
})

const dueLabel = (row) => (row.overdue ? 'Overdue' : row.due_out_today ? 'Due out' : 'Staying')
const dueTheme = (row) => (row.overdue ? 'red' : row.due_out_today ? 'orange' : 'green')

const columns = [
  { label: 'Guest', key: 'guest_name', width: 2 },
  { label: 'Room', key: 'room_number' },
  { label: 'Type', key: 'room_type' },
  { label: 'In', key: 'actual_check_in', getLabel: ({ row }) => date(row.actual_check_in) },
  {
    label: 'Due out',
    key: 'expected_check_out',
    getLabel: ({ row }) => date(row.expected_check_out),
  },
  { label: 'Nights', key: 'nights', align: 'right' },
  {
    label: 'Amount',
    key: 'total_amount',
    align: 'right',
    getLabel: ({ row }) => currency(row.total_amount),
  },
  { label: 'Due', key: 'due', getLabel: ({ row }) => dueLabel(row) },
]

const showStay = ref(false)
const showKeys = ref(false)
const selected = ref({})
const keyEncodingEnabled = computed(() => Boolean(cardSettings.data?.key_encoding?.enabled))

const detail = computed(() => {
  const s = selected.value
  return [
    { label: 'Room', value: s.room_number || '—' },
    { label: 'Room type', value: s.room_type || '—' },
    { label: 'Checked in', value: date(s.actual_check_in) || '—' },
    { label: 'Due out', value: date(s.expected_check_out) || '—' },
    { label: 'Nights', value: s.nights ?? '—' },
    { label: 'Guests', value: `${s.adults || 0} adults, ${s.children || 0} children` },
    { label: 'Amount', value: currency(s.total_amount) },
  ]
})

function open(row) {
  selected.value = row
  showStay.value = true
}

const checkOut = createResource({
  url: 'ihotel.frontend_api.check_out',
  onSuccess: () => {
    showStay.value = false
    toast.success('Guest checked out')
    inHouse.reload()
  },
})
</script>
