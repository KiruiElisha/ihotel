<template>
  <PageHeader title="Laundry">
    <template #actions>
      <Button
        label="Refresh"
        :loading="laundry.loading"
        :icon-left="LucideRefreshCw"
        @click="laundry.reload()"
      />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="select" size="sm" v-model="statusFilter" :options="statusChoices" />
    <FormControl type="text" size="sm" placeholder="Room or customer" v-model="search" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rows.length }} orders</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="laundry.error" />

    <div class="mb-5 grid grid-cols-2 gap-3 md:grid-cols-4">
      <StatTile label="Orders" :value="totals.orders ?? 0" />
      <StatTile label="In Progress" :value="totals.in_progress ?? 0" />
      <StatTile label="Ready" :value="totals.ready ?? 0" hint="Awaiting delivery" />
      <StatTile label="Outstanding" :value="currency(totals.outstanding)" hint="Unpaid" />
    </div>

    <ResponsiveList
      :columns="columns"
      :rows="rows"
      :empty-state="{ title: 'No laundry orders', description: 'Orders raised in the desk appear here.' }"
    >
      <template #card="{ row }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-ink-gray-9">
              {{ row.contact_person || row.customer || row.name }}
            </p>
            <p class="mt-0.5 text-sm text-ink-gray-5">
              <span v-if="row.room_number">Room {{ row.room_number }} &middot; </span>
              {{ row.service_type || 'Laundry' }}
            </p>
          </div>
          <StatusBadge :value="row.status" />
        </div>
        <dl class="mt-3 grid grid-cols-3 gap-2 border-t border-outline-gray-1 pt-3 text-sm">
          <div>
            <dt class="text-ink-gray-5">Ordered</dt>
            <dd class="text-ink-gray-8">{{ date(row.order_date) }}</dd>
          </div>
          <div>
            <dt class="text-ink-gray-5">Due</dt>
            <dd class="text-ink-gray-8">{{ date(row.expected_delivery) }}</dd>
          </div>
          <div>
            <dt class="text-ink-gray-5">Total</dt>
            <dd class="tabular-nums text-ink-gray-8">{{ currency(row.total_amount) }}</dd>
          </div>
        </dl>
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
import { lists } from '@/data/lists'
import { currency, date } from '@/data/format'

const laundry = createResource({
  url: 'ihotel.frontend_api.get_laundry',
  auto: true,
})

const statusFilter = ref('')
const search = ref('')

const totals = computed(() => laundry.data?.totals || {})

const statusChoices = computed(() => [
  { label: 'All statuses', value: '' },
  ...(lists.data?.laundry_statuses || []).map((s) => ({ label: s, value: s })),
])

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  return (laundry.data?.orders || []).filter((row) => {
    if (statusFilter.value && row.status !== statusFilter.value) return false
    if (!q) return true
    return [row.room_number, row.customer, row.contact_person].some((v) =>
      String(v || '').toLowerCase().includes(q),
    )
  })
})

const columns = [
  { label: 'Order', key: 'name' },
  {
    label: 'Customer',
    key: 'contact_person',
    width: 2,
    getLabel: ({ row }) => row.contact_person || row.customer || '—',
  },
  { label: 'Room', key: 'room_number' },
  { label: 'Service', key: 'service_type' },
  { label: 'Due', key: 'expected_delivery', getLabel: ({ row }) => date(row.expected_delivery) },
  {
    label: 'Total',
    key: 'total_amount',
    align: 'right',
    getLabel: ({ row }) => currency(row.total_amount),
  },
  { label: 'Status', key: 'status', type: 'badge' },
]

</script>
