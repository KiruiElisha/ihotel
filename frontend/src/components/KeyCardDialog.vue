<template>
  <Dialog v-model="show" :options="{ title: 'Room Keys', size: 'lg' }">
    <template #body-content>
      <div v-if="!settings.key_encoding?.enabled" class="rounded-md bg-surface-gray-2 p-3 text-sm text-ink-gray-6">
        Key encoding is disabled in iHotel Settings → Card Integration.
      </div>

      <template v-else>
        <!-- Encode form -->
        <div class="rounded-lg border border-outline-gray-2 p-3">
          <div class="mb-3 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-ink-gray-8">Issue a key</h3>
            <Badge :label="`Lock system: ${settings.key_encoding?.vendor || 'Mock'}`" theme="gray" />
          </div>

          <div class="grid gap-3 sm:grid-cols-2">
            <FormControl label="Room" :modelValue="roomLabel" disabled />
            <FormControl
              type="select"
              label="Access level"
              v-model="form.access_level"
              :options="accessOptions"
            />
            <div>
              <label class="mb-1 block text-sm text-ink-gray-6">Valid from</label>
              <input v-model="form.valid_from" type="datetime-local" class="ihotel-dt" />
            </div>
            <div>
              <label class="mb-1 block text-sm text-ink-gray-6">Valid to</label>
              <input v-model="form.valid_to" type="datetime-local" class="ihotel-dt" />
            </div>
          </div>

          <label class="mt-3 flex items-center gap-2 text-sm text-ink-gray-7">
            <input v-model="form.is_duplicate" type="checkbox" class="rounded" />
            Duplicate key (issue an extra key without invalidating existing ones)
          </label>

          <ErrorMessage class="mt-2" :message="encodeError" />
          <Button
            class="mt-3"
            variant="solid"
            theme="blue"
            :icon-left="LucideKeyRound"
            label="Encode key"
            :loading="encoding"
            :disabled="!room"
            @click="onEncode"
          />
        </div>

        <!-- Issued keys -->
        <div class="mt-4">
          <h3 class="mb-2 text-sm font-semibold text-ink-gray-8">Issued keys</h3>
          <ErrorMessage class="mb-2" :message="listError" />
          <p v-if="!keys.length && !loadingKeys" class="text-sm text-ink-gray-5">No keys issued yet.</p>
          <ul class="space-y-2">
            <li
              v-for="k in keys"
              :key="k.name"
              class="flex items-center justify-between gap-3 rounded-md border border-outline-gray-2 p-2.5"
            >
              <div class="min-w-0">
                <p class="flex items-center gap-2 truncate font-mono text-xs text-ink-gray-8">
                  {{ k.card_uid || '—' }}
                  <Badge :label="k.status" :theme="statusTheme(k.status)" />
                  <Badge v-if="k.is_duplicate" label="Duplicate" theme="gray" />
                </p>
                <p class="mt-0.5 truncate text-xs text-ink-gray-5">
                  {{ k.access_level }} · {{ fmt(k.valid_from) }} → {{ fmt(k.valid_to) }}
                </p>
              </div>
              <Button
                v-if="k.status !== 'Cancelled'"
                size="sm"
                theme="red"
                label="Cancel"
                :loading="cancelling === k.name"
                @click="onCancel(k)"
              />
            </li>
          </ul>
        </div>
      </template>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Badge, Button, Dialog, ErrorMessage, FormControl, toast } from 'frappe-ui'
import LucideKeyRound from '~icons/lucide/key-round'
import { cardSettings, encodeKey, cancelKey, listKeys } from '@/data/cards'
import { date as fmtDate } from '@/data/format'

const props = defineProps({
  room: { type: String, default: null },
  roomLabel: { type: String, default: '' },
  guest: { type: String, default: null },
  reservation: { type: String, default: null },
  checkedIn: { type: String, default: null },
  validFrom: { type: String, default: null },
  validTo: { type: String, default: null },
})
const show = defineModel({ type: Boolean, default: false })

const settings = computed(() => cardSettings.data || {})
const accessOptions = computed(() =>
  (settings.value.key_encoding?.access_levels || ['Guest']).map((l) => ({ label: l, value: l })),
)

const form = reactive({ access_level: 'Guest', valid_from: '', valid_to: '', is_duplicate: false })
const keys = ref([])
const encoding = ref(false)
const loadingKeys = ref(false)
const cancelling = ref('')
const encodeError = ref('')
const listError = ref('')

// Prefill the validity window from the stay and refresh the key list on open.
watch(show, (open) => {
  if (!open) return
  form.access_level = settings.value.key_encoding?.default_access_level || 'Guest'
  form.is_duplicate = false
  form.valid_from = toLocalInput(props.validFrom) || toLocalInput(new Date())
  form.valid_to = toLocalInput(props.validTo)
  refreshKeys()
})

async function refreshKeys() {
  if (!props.room && !props.reservation && !props.checkedIn && !props.guest) return
  loadingKeys.value = true
  listError.value = ''
  try {
    keys.value = await listKeys({
      room: props.room,
      reservation: props.reservation,
      checked_in: props.checkedIn,
      guest: props.guest,
    })
  } catch (e) {
    listError.value = e?.messages?.[0] || e?.message || 'Could not load keys.'
  } finally {
    loadingKeys.value = false
  }
}

async function onEncode() {
  encoding.value = true
  encodeError.value = ''
  try {
    await encodeKey({
      room: props.room,
      guest: props.guest,
      reservation: props.reservation,
      checked_in: props.checkedIn,
      access_level: form.access_level,
      valid_from: toBackendDt(form.valid_from),
      valid_to: toBackendDt(form.valid_to),
      is_duplicate: form.is_duplicate ? 1 : 0,
    })
    toast.success('Key encoded')
    form.is_duplicate = false
    await refreshKeys()
  } catch (e) {
    encodeError.value = e?.messages?.[0] || e?.message || 'Could not encode the key.'
  } finally {
    encoding.value = false
  }
}

async function onCancel(k) {
  cancelling.value = k.name
  try {
    await cancelKey(k.name)
    toast.success('Key cancelled')
    await refreshKeys()
  } catch (e) {
    toast.error(e?.messages?.[0] || e?.message || 'Could not cancel the key.')
  } finally {
    cancelling.value = ''
  }
}

function statusTheme(status) {
  return { Encoded: 'green', Active: 'green', Cancelled: 'gray', Expired: 'orange', Failed: 'red' }[status] || 'gray'
}

const fmt = (v) => (v ? fmtDate(v) : '—')

// datetime-local <-> backend helpers ("YYYY-MM-DDTHH:MM" <-> "YYYY-MM-DD HH:MM:SS").
function toLocalInput(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}
function toBackendDt(value) {
  if (!value) return null
  return value.replace('T', ' ') + (value.length === 16 ? ':00' : '')
}
</script>

<style scoped>
.ihotel-dt {
  width: 100%;
  border-radius: 0.375rem;
  border: 1px solid var(--outline-gray-2, #d1d5db);
  background: var(--surface-gray-1, #fff);
  padding: 0.375rem 0.5rem;
  font-size: 0.875rem;
  color: var(--ink-gray-8, #1f272e);
}
</style>
