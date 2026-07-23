<template>
  <PageHeader title="Reservations">
    <template #actions>
      <Button label="New" variant="solid" theme="blue" :icon-left="LucidePlus" @click="openNew" />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="select" size="sm" v-model="statusFilter" :options="statusChoices" />
    <FormControl type="text" size="sm" placeholder="Search guest" v-model="search" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rows.length }} bookings</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="reservations.error" />

    <ResponsiveList
      :columns="columns"
      :rows="rows"
      :on-row-click="openEdit"
      :empty-state="{ title: 'No reservations', description: 'Take a booking to get started.' }"
    >
      <template #card="{ row }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-ink-gray-9">{{ row.guest_name }}</p>
            <p class="mt-0.5 text-sm text-ink-gray-5">{{ row.room_type || 'No room type' }}</p>
          </div>
          <Badge :theme="statusTheme(row.status)">{{ statusLabel(row.status) }}</Badge>
        </div>
        <dl class="mt-3 grid grid-cols-3 gap-2 border-t border-outline-gray-1 pt-3 text-sm">
          <div>
            <dt class="text-ink-gray-5">Arrives</dt>
            <dd class="text-ink-gray-8">{{ date(row.check_in_date) }}</dd>
          </div>
          <div>
            <dt class="text-ink-gray-5">Nights</dt>
            <dd class="tabular-nums text-ink-gray-8">
              {{ row.days || nights(row.check_in_date, row.check_out_date) }}
            </dd>
          </div>
          <div>
            <dt class="text-ink-gray-5">Total</dt>
            <dd class="tabular-nums text-ink-gray-8">{{ currency(row.total_charges) }}</dd>
          </div>
        </dl>
      </template>
    </ResponsiveList>
  </div>

  <Dialog
    v-model="showDialog"
    :options="{ title: draft.name ? 'Edit Reservation' : 'New Reservation', size: 'lg' }"
  >
    <template #body-content>
      <div class="space-y-4">
        <FormControl
          type="select"
          label="Guest"
          v-model="draft.guest"
          :options="guestChoices"
          description="Add the guest under Guests first if they are new."
          required
        />
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl
            type="select"
            label="Room type"
            v-model="draft.room_type"
            :options="roomTypeChoices"
          />
          <FormControl
            type="select"
            label="Status"
            v-model="draft.status"
            :options="statusOptions"
          />
        </div>
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl type="date" label="Arrival" v-model="draft.check_in_date" required />
          <FormControl type="date" label="Departure" v-model="draft.check_out_date" required />
        </div>
        <div class="grid gap-4 sm:grid-cols-3">
          <FormControl type="number" label="Adults" v-model="draft.adults" />
          <FormControl type="number" label="Children" v-model="draft.children" />
          <FormControl type="number" label="Total charges" v-model="draft.total_charges" />
        </div>
        <p v-if="stayLength" class="text-sm text-ink-gray-6">{{ stayLength }}</p>
        <ErrorMessage :message="save.error" />
      </div>
    </template>
    <template #actions>
      <Button
        class="w-full"
        variant="solid"
        theme="blue"
        label="Save"
        :loading="save.loading"
        @click="submit"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Badge, Button, Dialog, ErrorMessage, FormControl, createResource, toast } from 'frappe-ui'
import LucidePlus from '~icons/lucide/plus'
import PageHeader from '@/components/PageHeader.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import { lists } from '@/data/lists'
import { currency, date, daysFromToday, nights, today } from '@/data/format'

const reservations = createResource({
  url: 'ihotel.frontend_api.get_reservations',
  auto: true,
})

const statusFilter = ref('')
const search = ref('')

const statusOptions = computed(() =>
  (lists.data?.reservation_statuses || []).map((s) => ({ label: statusLabel(s), value: s })),
)
const statusChoices = computed(() => [
  { label: 'All statuses', value: '' },
  ...statusOptions.value,
])
const roomTypeChoices = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.room_types || []).map((t) => ({ label: t, value: t })),
])
const guestChoices = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.guests || []).map((g) => ({ label: g.guest_name || g.name, value: g.name })),
])

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  return (reservations.data || []).filter((row) => {
    if (statusFilter.value && row.status !== statusFilter.value) return false
    if (!q) return true
    return String(row.guest_name || '').toLowerCase().includes(q)
  })
})

const columns = [
  { label: 'Guest', key: 'guest_name', width: 2 },
  { label: 'Room type', key: 'room_type' },
  { label: 'Arrives', key: 'check_in_date', getLabel: ({ row }) => date(row.check_in_date) },
  { label: 'Departs', key: 'check_out_date', getLabel: ({ row }) => date(row.check_out_date) },
  {
    label: 'Nights',
    key: 'nights',
    align: 'right',
    getLabel: ({ row }) => row.days || nights(row.check_in_date, row.check_out_date),
  },
  {
    label: 'Total',
    key: 'total_charges',
    align: 'right',
    getLabel: ({ row }) => currency(row.total_charges),
  },
  { label: 'Status', key: 'status', getLabel: ({ row }) => statusLabel(row.status) },
]

// Reservation.status is stored lowercase (pending / confirmed / checked_in /
// cancelled); present it in words without changing what is saved.
const STATUS_LABELS = {
  pending: 'Pending',
  confirmed: 'Confirmed',
  checked_in: 'Checked in',
  cancelled: 'Cancelled',
}
const statusLabel = (status) => STATUS_LABELS[status] || status || 'Pending'

const statusTheme = (status) =>
  ({ confirmed: 'green', checked_in: 'green', pending: 'orange', cancelled: 'red' })[status] ||
  'gray'

const showDialog = ref(false)
const draft = reactive({})

const stayLength = computed(() => {
  const n = nights(draft.check_in_date, draft.check_out_date)
  if (!n) return ''
  return `${n} night${n === 1 ? '' : 's'}.`
})

function openNew() {
  Object.assign(draft, {
    name: null,
    guest: '',
    room_type: '',
    status: statusOptions.value[0]?.value || '',
    check_in_date: today(),
    check_out_date: daysFromToday(1),
    adults: 1,
    children: 0,
    total_charges: 0,
  })
  showDialog.value = true
}

function openEdit(row) {
  Object.assign(draft, { ...row })
  showDialog.value = true
}

const save = createResource({
  url: 'ihotel.frontend_api.save_doc',
  onSuccess: () => {
    showDialog.value = false
    toast.success('Reservation saved')
    reservations.reload()
  },
})

function submit() {
  const { name, guest_name, creation, ...values } = draft
  save.submit({ doctype: 'Reservation', name: name || null, values })
}
</script>
