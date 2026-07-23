<template>
  <Dialog v-model="show" :options="{ title: 'Scan ID / Passport', size: 'lg' }">
    <template #body-content>
      <!-- Document type -->
      <div class="mb-4 flex gap-2">
        <Button
          v-for="m in modes"
          :key="m.value"
          :variant="mode === m.value ? 'solid' : 'subtle'"
          :theme="mode === m.value ? 'blue' : 'gray'"
          :label="m.label"
          class="flex-1"
          @click="setMode(m.value)"
        />
      </div>

      <!-- Camera -->
      <div class="overflow-hidden rounded-lg border border-outline-gray-2 bg-black">
        <video
          ref="videoEl"
          class="aspect-[16/10] w-full object-cover"
          :class="{ hidden: !camera.active.value }"
          playsinline
          muted
        ></video>
        <div
          v-if="!camera.active.value"
          class="flex aspect-[16/10] w-full flex-col items-center justify-center gap-2 text-ink-gray-4"
        >
          <LucideCamera class="h-8 w-8" />
          <span class="text-sm">Camera off</span>
        </div>
      </div>

      <div class="mt-2 flex flex-wrap gap-2">
        <Button
          v-if="!camera.active.value"
          :icon-left="LucideCamera"
          label="Start camera"
          @click="camera.start()"
        />
        <template v-else>
          <Button variant="solid" theme="blue" :icon-left="LucideScanLine" label="Capture" @click="onCapture" />
          <Button label="Stop" @click="camera.stop()" />
        </template>
        <span v-if="frontImage" class="self-center text-sm text-ink-green-3">✓ Image captured</span>
      </div>
      <ErrorMessage class="mt-2" :message="camera.error.value" />

      <!-- Raw text: filled by the decoder, or typed/pasted by staff -->
      <div class="mt-4">
        <label class="mb-1 block text-sm text-ink-gray-6">
          {{ mode === 'mrz' ? 'Passport / ID machine-readable zone (2–3 lines)' : 'Driver-license barcode text' }}
        </label>
        <textarea
          v-model="rawText"
          rows="3"
          spellcheck="false"
          class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 p-2 font-mono text-xs text-ink-gray-8"
          :placeholder="mode === 'mrz' ? 'P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<\nL898902C36UTO7408122F1204159...' : 'Auto-filled on capture, or paste the decoded barcode'"
        ></textarea>
        <p class="mt-1 text-xs text-ink-gray-5">
          {{ mode === 'mrz'
            ? 'Type the lines from the bottom of the passport / ID if the camera can’t read them.'
            : 'Capture attempts to read the PDF417 barcode automatically.' }}
        </p>
      </div>

      <div class="mt-3 flex gap-2">
        <Button
          variant="solid"
          theme="gray"
          label="Read document"
          :loading="reading"
          :disabled="!rawText.trim()"
          @click="onRead"
        />
        <Button v-if="parsed" label="Clear" @click="reset" />
      </div>
      <ErrorMessage class="mt-2" :message="error" />

      <!-- Parsed review -->
      <div v-if="parsed" class="mt-4 rounded-lg border border-outline-gray-2 p-3">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-ink-gray-8">Review scanned details</h3>
          <Badge v-if="!parsed.valid" theme="orange" label="Check digits failed — verify manually" />
          <Badge v-else theme="green" label="Verified" />
        </div>
        <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <div v-for="f in reviewRows" :key="f.label" class="min-w-0">
            <dt class="text-ink-gray-5">{{ f.label }}</dt>
            <dd class="truncate font-medium text-ink-gray-9">{{ f.value || '—' }}</dd>
          </div>
        </dl>
      </div>
    </template>

    <template #actions>
      <Button
        class="w-full"
        variant="solid"
        theme="blue"
        :label="guest ? 'Apply & save to guest' : 'Use these details'"
        :loading="applying"
        :disabled="!parsed"
        @click="onApply"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Badge, Button, Dialog, ErrorMessage, toast } from 'frappe-ui'
import LucideCamera from '~icons/lucide/camera'
import LucideScanLine from '~icons/lucide/scan-line'
import { useCamera } from '@/composables/useCamera'
import { scanId, applyIdToGuest } from '@/data/cards'
import { decodePdf417FromImage } from '@/utils/barcode'

const props = defineProps({
  // When set, parsed fields + images are saved straight to this Guest.
  // When null, the dialog emits `filled` so a parent form can populate itself.
  guest: { type: String, default: null },
})
const emit = defineEmits(['applied', 'filled'])
const show = defineModel({ type: Boolean, default: false })

const modes = [
  { label: 'Passport / ID', value: 'mrz' },
  { label: 'Driver License', value: 'barcode' },
]
const mode = ref('mrz')

const camera = useCamera()
const videoEl = camera.videoEl

const rawText = ref('')
const frontImage = ref('')
const parsed = ref(null)
const reading = ref(false)
const applying = ref(false)
const error = ref('')

function setMode(value) {
  mode.value = value
  parsed.value = null
  error.value = ''
}

async function onCapture() {
  error.value = ''
  const img = camera.capture()
  if (!img) {
    error.value = 'Nothing captured — is the camera ready?'
    return
  }
  frontImage.value = img
  if (mode.value === 'barcode') {
    try {
      rawText.value = await decodePdf417FromImage(img)
      toast.success('Barcode read')
    } catch (e) {
      error.value = e?.message || 'Could not read the barcode; enter it manually.'
    }
  }
}

async function onRead() {
  reading.value = true
  error.value = ''
  parsed.value = null
  try {
    parsed.value = await scanId(rawText.value)
  } catch (e) {
    error.value = e?.messages?.[0] || e?.message || 'Could not parse this document.'
  } finally {
    reading.value = false
  }
}

const reviewRows = computed(() => {
  const p = parsed.value
  if (!p) return []
  return [
    { label: 'Name', value: p.full_name },
    { label: 'Document type', value: p.guest_fields?.id_type },
    { label: 'Document number', value: p.document_number },
    { label: 'Date of birth', value: p.date_of_birth },
    { label: 'Expiry', value: p.expiry_date },
    { label: 'Sex', value: p.sex },
    { label: 'Nationality', value: p.guest_fields?.nationality || p.nationality_code },
  ]
})

async function onApply() {
  if (!parsed.value) return
  applying.value = true
  error.value = ''
  try {
    if (props.guest) {
      const res = await applyIdToGuest({
        data: parsed.value,
        guest: props.guest,
        frontImage: frontImage.value,
      })
      toast.success('Guest updated from scan')
      emit('applied', res)
    } else {
      emit('filled', { fields: parsed.value.guest_fields, data: parsed.value, frontImage: frontImage.value })
    }
    close()
  } catch (e) {
    error.value = e?.messages?.[0] || e?.message || 'Could not apply the scan.'
  } finally {
    applying.value = false
  }
}

function reset() {
  parsed.value = null
  rawText.value = ''
  frontImage.value = ''
  error.value = ''
}

function close() {
  camera.stop()
  reset()
  show.value = false
}
</script>
