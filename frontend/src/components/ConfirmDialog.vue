<template>
  <Dialog v-model="show" :options="{ title }">
    <template #body-content>
      <p class="text-base text-ink-gray-7">{{ message }}</p>
      <ErrorMessage class="mt-3" :message="error" />
    </template>
    <template #actions>
      <div class="flex gap-2">
        <Button class="flex-1" label="Cancel" @click="show = false" />
        <Button
          class="flex-1"
          variant="solid"
          :theme="theme"
          :label="confirmLabel"
          :loading="loading"
          @click="$emit('confirm')"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Button, Dialog, ErrorMessage } from 'frappe-ui'

defineProps({
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirm' },
  theme: { type: String, default: 'red' },
  loading: { type: Boolean, default: false },
  error: { type: [String, Object], default: null },
})

defineEmits(['confirm'])

const show = defineModel({ type: Boolean, default: false })
</script>
