<template>
  <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4">
    <p class="text-sm text-ink-gray-5">{{ label }}</p>
    <p class="mt-2 text-2xl font-semibold tabular-nums" :class="valueClass">
      {{ value }}
    </p>
    <p v-if="hint" class="mt-1 text-xs text-ink-gray-5">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  hint: { type: String, default: '' },
  // Colour the figure by sign when it represents a gain or loss.
  signed: { type: Boolean, default: false },
  amount: { type: Number, default: null },
})

const valueClass = computed(() => {
  if (!props.signed || props.amount === null) return 'text-ink-gray-9'
  if (props.amount > 0) return 'text-ink-green-3'
  if (props.amount < 0) return 'text-ink-red-3'
  return 'text-ink-gray-9'
})
</script>
