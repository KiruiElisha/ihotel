<template>
  <PageHeader title="Today">
    <template #actions>
      <Button
        label="Refresh"
        :loading="today.loading"
        :icon-left="LucideRefreshCw"
        @click="today.reload()"
      />
    </template>
  </PageHeader>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="today.error" />

    <div v-if="d" class="space-y-6">
      <section>
        <h2 class="mb-3 text-sm font-medium text-ink-gray-7">Occupancy</h2>
        <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatTile
            label="Occupancy"
            tone="blue"
            :value="percent(d.rooms.occupancy_pct, 0)"
            :hint="`${d.rooms.occupied} of ${d.rooms.total} rooms`"
          />
          <StatTile label="Available" tone="green" :value="d.rooms.available" hint="Ready to sell" />
          <StatTile label="In House" :value="d.in_house" hint="Guests staying now" />
          <StatTile
            label="Revenue Today"
            :value="currency(d.revenue_today)"
            hint="Checked-in today"
          />
        </div>
      </section>

      <section>
        <h2 class="mb-3 text-sm font-medium text-ink-gray-7">Performance</h2>
        <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatTile label="ADR" :value="currency(d.adr)" hint="Average per occupied room" />
          <StatTile label="RevPAR" :value="currency(d.revpar)" hint="Per available room" />
          <StatTile
            label="Arrivals Pending"
            :tone="d.arrivals_pending ? 'orange' : 'white'"
            :value="d.arrivals_pending"
            :hint="`${d.arrivals.length} due in today`"
          />
          <StatTile
            label="Rooms to Clean"
            :tone="d.rooms.dirty ? 'orange' : 'white'"
            :value="d.rooms.dirty"
            :hint="d.rooms.out_of_order ? `${d.rooms.out_of_order} out of order` : 'None out of order'"
          />
        </div>
      </section>

      <section>
        <h2 class="mb-3 text-sm font-medium text-ink-gray-7">Workload</h2>
        <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatTile
            label="Housekeeping Open"
            :value="d.housekeeping_open"
            :hint="`${percent(d.housekeeping_pct, 0)} done`"
          />
          <StatTile label="Housekeeping Done" tone="green" :value="d.housekeeping_done" />
          <StatTile
            label="Maintenance Open"
            :tone="d.maintenance_open ? 'red' : 'white'"
            :value="d.maintenance_open"
          />
          <StatTile label="Departures" :value="d.departures.length" hint="Due out today" />
        </div>
      </section>

      <section>
        <h2 class="mb-3 text-sm font-medium text-ink-gray-7">Room status</h2>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="(count, status) in d.rooms.by_status"
            :key="status"
            class="rounded-lg border border-outline-gray-1 px-3 py-2 text-sm"
          >
            <span class="text-ink-gray-5">{{ status }}</span>
            <span class="ml-2 font-semibold tabular-nums text-ink-gray-9">{{ count }}</span>
          </div>
          <p v-if="!Object.keys(d.rooms.by_status).length" class="text-sm text-ink-gray-5">
            No rooms set up yet.
          </p>
        </div>
      </section>

      <div class="grid gap-5 lg:grid-cols-2">
        <section>
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-sm font-medium text-ink-gray-7">
              Arriving today
              <span class="ml-1 text-ink-gray-5">({{ d.arrivals.length }})</span>
            </h2>
            <Button
              label="All bookings"
              variant="ghost"
              @click="$router.push({ name: 'Reservations' })"
            />
          </div>
          <ResponsiveList
            :columns="movementColumns"
            :rows="d.arrivals"
            :empty-state="{ title: 'No arrivals today', description: 'A quiet morning.' }"
          >
            <template #card="{ row }">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate font-medium text-ink-gray-9">{{ row.guest_name }}</p>
                  <p class="mt-0.5 text-sm text-ink-gray-5">{{ row.room_type || '—' }}</p>
                </div>
                <StatusBadge :value="row.status" />
              </div>
            </template>
          </ResponsiveList>
        </section>

        <section>
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-sm font-medium text-ink-gray-7">
              Departing today
              <span class="ml-1 text-ink-gray-5">({{ d.departures.length }})</span>
            </h2>
            <Button label="Room board" variant="ghost" @click="$router.push({ name: 'RoomBoard' })" />
          </div>
          <ResponsiveList
            :columns="movementColumns"
            :rows="d.departures"
            :empty-state="{ title: 'No departures today', description: 'Nobody is due out.' }"
          >
            <template #card="{ row }">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate font-medium text-ink-gray-9">{{ row.guest_name }}</p>
                  <p class="mt-0.5 text-sm text-ink-gray-5">{{ row.room_type || '—' }}</p>
                </div>
                <StatusBadge :value="row.status" />
              </div>
            </template>
          </ResponsiveList>
        </section>
      </div>

      <section>
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-medium text-ink-gray-7">Recent activity</h2>
          <Badge v-if="d.housekeeping_open" theme="orange">
            {{ d.housekeeping_open }} housekeeping open
          </Badge>
        </div>
        <div class="rounded-lg border border-outline-gray-1">
          <p v-if="!d.activity.length" class="p-6 text-center text-sm text-ink-gray-6">
            Nothing in the last two days.
          </p>
          <ul v-else class="divide-y divide-outline-gray-1">
            <li v-for="item in d.activity" :key="`${item.type}-${item.name}`" class="flex gap-3 p-3">
              <span
                class="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg"
                :class="activityTint(item.type)"
                aria-hidden="true"
              >
                <component :is="activityIcon(item.type)" class="size-4" />
              </span>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-ink-gray-9">{{ item.title }}</p>
                <p class="truncate text-sm text-ink-gray-6">{{ item.description }}</p>
              </div>
              <span class="shrink-0 text-xs text-ink-gray-5">{{ timeAgo(item.on) }}</span>
            </li>
          </ul>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge, Button, ErrorMessage, createResource } from 'frappe-ui'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideLogIn from '~icons/lucide/log-in'
import LucideLogOut from '~icons/lucide/log-out'
import LucideCalendarPlus from '~icons/lucide/calendar-plus'
import PageHeader from '@/components/PageHeader.vue'
import StatTile from '@/components/StatTile.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { currency, date, percent, timeAgo } from '@/data/format'

const today = createResource({
  url: 'ihotel.frontend_api.get_today',
  auto: true,
})

const d = computed(() => today.data)

const movementColumns = [
  { label: 'Guest', key: 'guest_name', width: 2 },
  { label: 'Room type', key: 'room_type' },
  { label: 'Arrives', key: 'check_in_date', getLabel: ({ row }) => date(row.check_in_date) },
  { label: 'Departs', key: 'check_out_date', getLabel: ({ row }) => date(row.check_out_date) },
  { label: 'Status', key: 'status', type: 'badge' },
]


const activityIcon = (type) =>
  ({ check_in: LucideLogIn, check_out: LucideLogOut, reservation: LucideCalendarPlus })[type] ||
  LucideCalendarPlus

const activityTint = (type) =>
  ({
    check_in: 'bg-green-100 text-green-700',
    check_out: 'bg-navy-50 text-navy-500',
    reservation: 'bg-brass-50 text-brass-600',
  })[type] || 'bg-surface-gray-2 text-ink-gray-6'
</script>
