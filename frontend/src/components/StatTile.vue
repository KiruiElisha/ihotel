<template>
  <div class="rounded-lg border p-4 transition-colors" :class="tone.card">
    <div class="flex items-start justify-between gap-2">
      <p class="text-sm" :class="tone.label">{{ label }}</p>
      <span v-if="icon" class="rounded-md p-1" :class="tone.icon">
        <component :is="icon" class="size-4" />
      </span>
    </div>
    <p class="mt-2 text-2xl font-semibold tabular-nums" :class="valueClass">
      {{ value }}
    </p>
    <p v-if="hint" class="mt-1 text-xs" :class="tone.hint">{{ hint }}</p>
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
  // Card treatment. 'white' is the default; the others are light tints of the
  // app's semantic colours — kept at the 50 end of each ramp so a row of them
  // stays calm rather than shouting.
  tone: {
    type: String,
    default: 'white',
    validator: (v) => ['white', 'blue', 'green', 'orange', 'red', 'gray'].includes(v),
  },
  icon: { type: [Object, Function], default: null },
})

const TONES = {
  white: {
    card: 'border-outline-gray-1 bg-surface-white',
    label: 'text-ink-gray-5',
    value: 'text-ink-gray-9',
    hint: 'text-ink-gray-5',
    icon: 'bg-surface-gray-2 text-ink-gray-6',
  },
  blue: {
    card: 'border-navy-100 bg-navy-50',
    label: 'text-navy-500',
    value: 'text-navy-900',
    hint: 'text-navy-500',
    icon: 'bg-white/70 text-navy-500',
  },
  green: {
    card: 'border-green-100 bg-green-50',
    label: 'text-green-700',
    value: 'text-green-900',
    hint: 'text-green-700',
    icon: 'bg-white/70 text-green-700',
  },
  orange: {
    card: 'border-orange-100 bg-orange-50',
    label: 'text-orange-700',
    value: 'text-orange-900',
    hint: 'text-orange-700',
    icon: 'bg-white/70 text-orange-700',
  },
  red: {
    card: 'border-red-100 bg-red-50',
    label: 'text-red-700',
    value: 'text-red-900',
    hint: 'text-red-700',
    icon: 'bg-white/70 text-red-700',
  },
  gray: {
    card: 'border-outline-gray-2 bg-surface-gray-1',
    label: 'text-ink-gray-6',
    value: 'text-ink-gray-9',
    hint: 'text-ink-gray-5',
    icon: 'bg-surface-white text-ink-gray-6',
  },
}

const tone = computed(() => TONES[props.tone] || TONES.white)

const valueClass = computed(() => {
  // A signed figure always colours by sign; it overrides the tone's value ink.
  if (props.signed && props.amount !== null) {
    if (props.amount > 0) return 'text-ink-green-3'
    if (props.amount < 0) return 'text-ink-red-3'
  }
  return tone.value.value
})
</script>
