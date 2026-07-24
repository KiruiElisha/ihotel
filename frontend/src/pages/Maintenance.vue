<template>
  <PageHeader title="Maintenance">
    <template #actions>
      <Button label="New" variant="solid" theme="blue" :icon-left="LucidePlus" @click="openNew" />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="select" size="sm" v-model="statusFilter" :options="statusChoices" />
    <FormControl type="text" size="sm" placeholder="Room or description" v-model="search" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rows.length }} requests</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="maintenance.error" />

    <div class="mb-5 grid grid-cols-3 gap-3">
      <StatTile label="Open" :value="counts.open ?? 0" />
      <StatTile label="In Progress" :value="counts.in_progress ?? 0" />
      <StatTile label="Resolved" :value="counts.resolved ?? 0" />
    </div>

    <ResponsiveList
      :columns="columns"
      :rows="rows"
      :on-row-click="openEdit"
      :empty-state="{ title: 'Nothing to fix', description: 'Raise a request when something breaks.' }"
    >
      <template #card="{ row }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-ink-gray-9">Room {{ row.room_number }}</p>
            <p class="mt-0.5 text-sm text-ink-gray-5">{{ row.category || 'Uncategorised' }}</p>
          </div>
          <StatusBadge :value="row.status || 'Open'" />
        </div>
        <p v-if="row.description" class="mt-2 line-clamp-2 text-sm text-ink-gray-7">
          {{ row.description }}
        </p>
        <p class="mt-2 flex flex-wrap items-center gap-1.5 text-xs text-ink-gray-5">
          <StatusBadge v-if="row.priority" :value="row.priority" />
          <span v-if="row.assigned_to">&middot; {{ row.assigned_to }}</span>
        </p>
      </template>
    </ResponsiveList>
  </div>

  <Dialog
    v-model="showDialog"
    :options="{ title: draft.name ? 'Edit Request' : 'New Request', size: 'lg' }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl type="select" label="Room" v-model="draft.room" :options="roomChoices" />
          <FormControl
            type="select"
            label="Category"
            v-model="draft.category"
            :options="categoryChoices"
          />
        </div>
        <div class="grid gap-4 sm:grid-cols-3">
          <FormControl
            type="select"
            label="Priority"
            v-model="draft.priority"
            :options="priorityOptions"
          />
          <FormControl type="select" label="Type" v-model="draft.maintenance_type" :options="typeOptions" />
          <FormControl type="select" label="Status" v-model="draft.status" :options="statusOptions" />
        </div>
        <FormControl type="textarea" :rows="3" label="Description" v-model="draft.description" />
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl type="date" label="Scheduled" v-model="draft.scheduled_date" />
          <FormControl type="number" label="Estimated cost" v-model="draft.estimated_cost" />
        </div>
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
import { Button, Dialog, ErrorMessage, FormControl, createResource, toast } from 'frappe-ui'
import LucidePlus from '~icons/lucide/plus'
import PageHeader from '@/components/PageHeader.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import StatTile from '@/components/StatTile.vue'
import { lists } from '@/data/lists'
import { currency, date } from '@/data/format'

const maintenance = createResource({
  url: 'ihotel.frontend_api.get_maintenance',
  auto: true,
})

const statusFilter = ref('')
const search = ref('')

const counts = computed(() => maintenance.data?.counts || {})

const statusOptions = computed(() =>
  (lists.data?.maintenance_statuses || []).map((s) => ({ label: s, value: s })),
)
const statusChoices = computed(() => [{ label: 'All statuses', value: '' }, ...statusOptions.value])
const priorityOptions = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.maintenance_priorities || []).map((p) => ({ label: p, value: p })),
])
const typeOptions = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.maintenance_types || []).map((t) => ({ label: t, value: t })),
])
const categoryChoices = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.maintenance_categories || []).map((c) => ({ label: c, value: c })),
])
const roomChoices = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.rooms || []).map((r) => ({ label: r.room_number || r.name, value: r.name })),
])

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  return (maintenance.data?.requests || []).filter((row) => {
    if (statusFilter.value && row.status !== statusFilter.value) return false
    if (!q) return true
    return [row.room_number, row.description, row.category].some((v) =>
      String(v || '').toLowerCase().includes(q),
    )
  })
})

const columns = [
  { label: 'Room', key: 'room_number' },
  { label: 'Category', key: 'category', width: 2 },
  { label: 'Priority', key: 'priority', type: 'badge' },
  { label: 'Assigned to', key: 'assigned_to' },
  {
    label: 'Reported',
    key: 'reported_date',
    getLabel: ({ row }) => date(row.reported_date),
  },
  {
    label: 'Est. cost',
    key: 'estimated_cost',
    align: 'right',
    getLabel: ({ row }) => (row.estimated_cost ? currency(row.estimated_cost) : ''),
  },
  { label: 'Status', key: 'status', type: 'badge' },
]


const showDialog = ref(false)
const draft = reactive({})

function openNew() {
  Object.assign(draft, {
    name: null,
    room: '',
    category: '',
    priority: 'Medium',
    maintenance_type: 'Reactive',
    status: 'Open',
    description: '',
    scheduled_date: '',
    estimated_cost: 0,
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
    toast.success('Request saved')
    maintenance.reload()
  },
})

function submit() {
  const { name, room_number, reported_date, ...values } = draft
  save.submit({ doctype: 'Maintenance Request', name: name || null, values })
}
</script>
