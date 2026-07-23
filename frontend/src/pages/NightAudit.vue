<template>
  <PageHeader title="Night Audit" />

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="audit.error" />

    <section v-if="tonight" class="mb-6">
      <h2 class="mb-3 text-sm font-medium text-ink-gray-7">
        Tonight &mdash; {{ date(tonight.audit_date) }}
      </h2>
      <div class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <StatTile label="Rooms" :value="tonight.total_rooms" />
        <StatTile label="Occupied" :value="tonight.occupied_rooms" />
        <StatTile label="Occupancy" :value="percent(tonight.occupancy_rate, 0)" />
        <StatTile label="ADR" :value="currency(tonight.adr)" hint="Per occupied room" />
        <StatTile label="RevPAR" :value="currency(tonight.revpar)" hint="Per available room" />
        <StatTile label="Revenue" :value="currency(tonight.total_revenue)" />
      </div>
      <p class="mt-3 text-xs text-ink-gray-5">
        Live figures for today. Running the audit in the desk records them against the date.
      </p>
    </section>

    <section>
      <h2 class="mb-3 text-sm font-medium text-ink-gray-7">Past audits</h2>
      <ResponsiveList
        :columns="columns"
        :rows="audits"
        :empty-state="{
          title: 'No audits recorded',
          description: 'Night audits run from the desk appear here.',
        }"
      >
        <template #card="{ row }">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="font-medium text-ink-gray-9">{{ date(row.audit_date) }}</p>
              <p class="mt-0.5 text-sm text-ink-gray-5">
                {{ row.occupied_rooms }} of {{ row.total_rooms }} rooms
              </p>
            </div>
            <span class="shrink-0 font-semibold tabular-nums text-ink-gray-9">
              {{ percent(row.occupancy_rate, 0) }}
            </span>
          </div>
          <dl class="mt-3 grid grid-cols-3 gap-2 border-t border-outline-gray-1 pt-3 text-sm">
            <div>
              <dt class="text-ink-gray-5">ADR</dt>
              <dd class="tabular-nums text-ink-gray-8">{{ currency(row.adr) }}</dd>
            </div>
            <div>
              <dt class="text-ink-gray-5">RevPAR</dt>
              <dd class="tabular-nums text-ink-gray-8">{{ currency(row.revpar) }}</dd>
            </div>
            <div>
              <dt class="text-ink-gray-5">Revenue</dt>
              <dd class="tabular-nums text-ink-gray-8">{{ currency(row.total_revenue) }}</dd>
            </div>
          </dl>
        </template>
      </ResponsiveList>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ErrorMessage, createResource } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import StatTile from '@/components/StatTile.vue'
import { currency, date, percent } from '@/data/format'

const audit = createResource({
  url: 'ihotel.frontend_api.get_night_audit',
  auto: true,
})

const tonight = computed(() => audit.data?.tonight)
const audits = computed(() => audit.data?.audits || [])

const columns = [
  { label: 'Date', key: 'audit_date', getLabel: ({ row }) => date(row.audit_date) },
  { label: 'Rooms', key: 'total_rooms', align: 'right' },
  { label: 'Occupied', key: 'occupied_rooms', align: 'right' },
  {
    label: 'Occupancy',
    key: 'occupancy_rate',
    align: 'right',
    getLabel: ({ row }) => percent(row.occupancy_rate, 0),
  },
  { label: 'ADR', key: 'adr', align: 'right', getLabel: ({ row }) => currency(row.adr) },
  { label: 'RevPAR', key: 'revpar', align: 'right', getLabel: ({ row }) => currency(row.revpar) },
  {
    label: 'Revenue',
    key: 'total_revenue',
    align: 'right',
    getLabel: ({ row }) => currency(row.total_revenue),
  },
]
</script>
