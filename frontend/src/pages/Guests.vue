<template>
  <PageHeader title="Guests">
    <template #actions>
      <Button label="New" variant="solid" theme="blue" :icon-left="LucidePlus" @click="openNew" />
    </template>
  </PageHeader>

  <div class="flex flex-wrap items-center gap-2 border-b border-outline-gray-1 px-4 py-2.5 sm:px-5">
    <FormControl type="text" size="sm" placeholder="Search name, email or phone" v-model="search" />
    <span class="ml-auto text-sm text-ink-gray-5">{{ rows.length }} guests</span>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="guests.error" />

    <ResponsiveList
      :columns="columns"
      :rows="rows"
      :on-row-click="openEdit"
      :empty-state="{ title: 'No guests', description: 'Add a guest to get started.' }"
    >
      <template #card="{ row }">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-medium text-ink-gray-9">{{ row.guest_name }}</p>
            <p class="mt-0.5 truncate text-sm text-ink-gray-5">{{ row.email || 'No email' }}</p>
          </div>
          <Avatar :label="row.guest_name" size="md" />
        </div>
        <p class="mt-2 text-sm text-ink-gray-6">
          {{ row.phone || 'No phone' }}
          <span v-if="row.nationality"> &middot; {{ row.nationality }}</span>
        </p>
      </template>
    </ResponsiveList>
  </div>

  <Dialog
    v-model="showDialog"
    :options="{ title: draft.name ? 'Edit Guest' : 'New Guest', size: 'lg' }"
  >
    <template #body-content>
      <div class="space-y-4">
        <FormControl type="text" label="Full name" v-model="draft.guest_name" required />
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl type="email" label="Email" v-model="draft.email" />
          <FormControl type="tel" label="Phone" v-model="draft.phone" />
        </div>
        <div class="grid gap-4 sm:grid-cols-2">
          <FormControl type="text" label="Address" v-model="draft.address_line_1" />
          <FormControl type="text" label="City" v-model="draft.city" />
        </div>
        <div class="grid gap-4 sm:grid-cols-3">
          <FormControl
            type="select"
            label="Nationality"
            v-model="draft.nationality"
            :options="countryChoices"
          />
          <FormControl type="select" label="ID type" v-model="draft.id_type" :options="idTypeChoices" />
          <FormControl type="text" label="ID number" v-model="draft.id_number" />
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
import {
  Avatar,
  Button,
  Dialog,
  ErrorMessage,
  FormControl,
  createResource,
  toast,
} from 'frappe-ui'
import LucidePlus from '~icons/lucide/plus'
import PageHeader from '@/components/PageHeader.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import { lists } from '@/data/lists'
import { date } from '@/data/format'

const guests = createResource({
  url: 'ihotel.frontend_api.get_guests',
  auto: true,
})

const search = ref('')

const countryChoices = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.countries || []).map((c) => ({ label: c, value: c })),
])
const idTypeChoices = computed(() => [
  { label: '', value: '' },
  ...(lists.data?.guest_id_types || []).map((t) => ({ label: t, value: t })),
])

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const data = guests.data || []
  if (!q) return data
  return data.filter((row) =>
    [row.guest_name, row.email, row.phone].some((v) => String(v || '').toLowerCase().includes(q)),
  )
})

const columns = [
  { label: 'Guest', key: 'guest_name', width: 2 },
  { label: 'Email', key: 'email', width: 2 },
  { label: 'Phone', key: 'phone' },
  { label: 'Nationality', key: 'nationality' },
  { label: 'Added', key: 'creation', getLabel: ({ row }) => date(row.creation) },
]

const showDialog = ref(false)
const draft = reactive({})

function openNew() {
  Object.assign(draft, {
    name: null,
    guest_name: '',
    email: '',
    phone: '',
    address_line_1: '',
    city: '',
    nationality: '',
    id_type: '',
    id_number: '',
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
    toast.success('Guest saved')
    guests.reload()
    // New guests must appear in the reservation form's picker.
    lists.reload()
  },
})

function submit() {
  const { name, creation, ...values } = draft
  save.submit({ doctype: 'Guest', name: name || null, values })
}
</script>
