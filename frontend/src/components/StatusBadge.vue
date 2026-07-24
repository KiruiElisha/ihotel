<template>
  <span
    class="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset"
    :class="statusTint(value)"
  >
    <span v-if="dot" class="size-1.5 rounded-full bg-current opacity-70" />
    {{ statusLabel(value) }}
  </span>
</template>

<script setup>
import { statusTint, statusLabel } from '@/data/status'

defineProps({
  value: { type: [String, Number], default: '' },
  // A leading dot reads better in dense tables; off for card layouts.
  dot: { type: Boolean, default: true },
})
</script>
