<template>
  <PageHeader title="Key Cards">
    <template #actions>
      <Button
        label="Refresh"
        :icon-left="LucideRefreshCw"
        :loading="keys.loading"
        @click="keys.reload()"
      />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="text" size="sm" placeholder="Search guest, room or card UID" v-model="search" />
    <FormControl type="select" size="sm" v-model="status" :options="statusOptions" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rows.length }} keys</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="keys.error" />

    <div class="mb-5 grid grid-cols-2 gap-3 md:grid-cols-4">
      <StatTile label="Total Issued" :value="totals.total || 0" tone="white" />
      <StatTile label="Active" :value="(totals.encoded || 0) + (totals.active || 0)" tone="green" hint="Currently valid" />
      <StatTile label="Expired" :value="totals.expired || 0" tone="orange" hint="Past validity" />
      <StatTile label="Failed" :value="totals.failed || 0" tone="red" hint="Encoding errors" />
    </div>

    <ResponsiveList
      :columns="columns"
      :rows="rows"
      :empty-state="{ title: 'No key cards', description: 'Encode a key from an in-house stay.' }"
    >
      <template #card="{ row }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-ink-gray-9">{{ row.guest_name || row.guest || '—' }}</p>
            <p class="mt-0.5 truncate text-sm text-ink-gray-5">Room {{ row.room }}</p>
          </div>
          <StatusBadge :value="row.status" />
        </div>
        <p class="mt-2 truncate font-mono text-xs text-ink-gray-6">{{ row.card_uid || '—' }}</p>
        <p class="mt-1 text-xs text-ink-gray-5">
          {{ row.access_level }} &middot; {{ date(row.valid_from) }} → {{ date(row.valid_to) }}
          <span v-if="row.is_duplicate"> &middot; Duplicate</span>
        </p>
      </template>
    </ResponsiveList>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Button, ErrorMessage, FormControl, createResource } from 'frappe-ui'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import PageHeader from '@/components/PageHeader.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import StatTile from '@/components/StatTile.vue'
import { date } from '@/data/format'

const keys = createResource({ url: 'ihotel.card_api.get_key_cards', auto: true })

const search = ref('')
const status = ref('')

const statusOptions = [
  { label: 'All statuses', value: '' },
  { label: 'Encoded', value: 'Encoded' },
  { label: 'Active', value: 'Active' },
  { label: 'Cancelled', value: 'Cancelled' },
  { label: 'Expired', value: 'Expired' },
  { label: 'Failed', value: 'Failed' },
]

const totals = computed(() => keys.data?.totals || {})

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  return (keys.data?.keys || []).filter((row) => {
    if (status.value && row.status !== status.value) return false
    if (!q) return true
    return [row.guest_name, row.room, row.card_uid].some((v) =>
      String(v || '').toLowerCase().includes(q),
    )
  })
})

const columns = [
  { label: 'Guest', key: 'guest_name', width: 2 },
  { label: 'Room', key: 'room' },
  { label: 'Card UID', key: 'card_uid', width: 2 },
  { label: 'Access', key: 'access_level' },
  { label: 'Status', key: 'status', type: 'badge' },
  { label: 'Valid from', key: 'valid_from', getLabel: ({ row }) => date(row.valid_from) },
  { label: 'Valid to', key: 'valid_to', getLabel: ({ row }) => date(row.valid_to) },
  { label: 'Vendor', key: 'vendor' },
]
</script>
