<template>
  <PageHeader title="Housekeeping">
    <template #actions>
      <Button label="New task" variant="solid" theme="blue" :icon-left="LucidePlus" @click="openNew" />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="select" size="sm" v-model="statusFilter" :options="statusChoices" />
    <FormControl type="text" size="sm" placeholder="Search room or notes" v-model="search" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rows.length }} tasks</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="housekeeping.error" />

    <div class="mb-5 grid grid-cols-3 gap-3">
      <StatTile label="Open" :value="counts.open ?? 0" />
      <StatTile label="In Progress" :value="counts.in_progress ?? 0" />
      <StatTile label="Completed" :value="counts.completed ?? 0" />
    </div>

    <ResponsiveList
      :columns="columns"
      :rows="rows"
      :on-row-click="openEdit"
      :empty-state="{ title: 'No tasks', description: 'Raise a task to get started.' }"
    >
      <template #card="{ row }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-ink-gray-9">
              Room {{ row.room || '—' }}
            </p>
            <p class="mt-0.5 text-sm text-ink-gray-5">{{ row.task_type || 'Task' }}</p>
          </div>
          <Badge :theme="statusTheme(row.status)">{{ row.status || 'Pending' }}</Badge>
        </div>
        <p v-if="row.notes" class="mt-2 text-sm text-ink-gray-7">{{ row.notes }}</p>
        <p class="mt-2 flex flex-wrap items-center gap-1.5 text-xs text-ink-gray-5">
          <Badge v-if="row.priority" size="sm" :theme="priorityTheme(row.priority)">
            {{ row.priority }}
          </Badge>
          <span v-if="row.assigned_to">&middot; {{ row.assigned_to }}</span>
        </p>
      </template>
    </ResponsiveList>
  </div>

  <Dialog
    v-model="showDialog"
    :options="{ title: draft.name ? 'Edit Task' : 'New Task', size: 'lg' }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl type="select" label="Room" v-model="draft.room" :options="roomChoices" />
          <FormControl
            type="select"
            label="Task type"
            v-model="draft.task_type"
            :options="taskTypeOptions"
          />
        </div>
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl
            type="select"
            label="Priority"
            v-model="draft.priority"
            :options="priorityOptions"
          />
          <FormControl
            type="select"
            label="Status"
            v-model="draft.status"
            :options="taskStatusOptions"
          />
        </div>
        <FormControl type="text" label="Assigned to" v-model="draft.assigned_to" />
        <FormControl type="textarea" :rows="3" label="Notes" v-model="draft.notes" />
        <ErrorMessage :message="save.error" />
      </div>
    </template>
    <template #actions>
      <div class="flex gap-2">
        <Button
          v-if="draft.name && draft.status !== 'Completed'"
          label="Mark done"
          theme="green"
          variant="subtle"
          :loading="markDone.loading"
          @click="markDone.submit({ task: draft.name, status: 'Completed' })"
        />
        <Button
          class="flex-1"
          variant="solid"
          theme="blue"
          label="Save"
          :loading="save.loading"
          @click="submit"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Badge, Button, Dialog, ErrorMessage, FormControl, createResource, toast } from 'frappe-ui'
import LucidePlus from '~icons/lucide/plus'
import PageHeader from '@/components/PageHeader.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import StatTile from '@/components/StatTile.vue'
import { lists } from '@/data/lists'
import { date } from '@/data/format'

const housekeeping = createResource({
  url: 'ihotel.frontend_api.get_housekeeping',
  auto: true,
})

const statusFilter = ref('')
const search = ref('')

const counts = computed(() => housekeeping.data?.counts || {})

const taskStatusOptions = computed(() =>
  (lists.data?.task_statuses || []).map((s) => ({ label: s, value: s })),
)
const statusChoices = computed(() => [
  { label: 'All statuses', value: '' },
  ...taskStatusOptions.value,
])
const taskTypeOptions = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.task_types || []).map((t) => ({ label: t, value: t })),
])
const priorityOptions = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.priorities || []).map((p) => ({ label: p, value: p })),
])
const roomChoices = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.rooms || []).map((r) => ({ label: r.room_number || r.name, value: r.name })),
])

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  return (housekeeping.data?.tasks || []).filter((row) => {
    if (statusFilter.value && row.status !== statusFilter.value) return false
    if (!q) return true
    return [row.room, row.notes, row.assigned_to].some((v) =>
      String(v || '').toLowerCase().includes(q),
    )
  })
})

const columns = [
  { label: 'Room', key: 'room' },
  { label: 'Task', key: 'task_type', width: 2 },
  { label: 'Priority', key: 'priority' },
  { label: 'Assigned to', key: 'assigned_to' },
  { label: 'Raised', key: 'creation', getLabel: ({ row }) => date(row.creation) },
  { label: 'Status', key: 'status' },
]

const statusTheme = (status) =>
  ({ Completed: 'green', 'In Progress': 'blue', Cancelled: 'gray' })[status] || 'orange'

const priorityTheme = (priority) =>
  ({ Urgent: 'red', High: 'orange', Normal: 'blue', Low: 'gray' })[priority] || 'gray'

const showDialog = ref(false)
const draft = reactive({})

function openNew() {
  Object.assign(draft, {
    name: null,
    room: '',
    task_type: '',
    priority: 'Normal',
    status: taskStatusOptions.value[0]?.value || 'Pending',
    assigned_to: '',
    notes: '',
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
    toast.success('Task saved')
    housekeeping.reload()
  },
})

const markDone = createResource({
  url: 'ihotel.frontend_api.set_task_status',
  onSuccess: () => {
    showDialog.value = false
    toast.success('Task completed')
    housekeeping.reload()
  },
})

function submit() {
  const { name, creation, completion_time, ...values } = draft
  save.submit({ doctype: 'Housekeeping Task', name: name || null, values })
}
</script>
