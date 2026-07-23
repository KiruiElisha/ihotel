<template>
  <Dropdown :options="options" placement="right">
    <slot :current="currentTheme">
      <Button variant="ghost" :label="`Theme: ${label}`" :icon-left="activeIcon" />
    </slot>
  </Dropdown>
</template>

<script setup>
import { computed } from 'vue'
import { Button, Dropdown, useTheme } from 'frappe-ui'
import LucideSun from '~icons/lucide/sun'
import LucideMoon from '~icons/lucide/moon'
import LucideMonitor from '~icons/lucide/monitor'
import LucideCheck from '~icons/lucide/check'

// frappe-ui persists the choice to localStorage and stamps data-theme on <html>,
// which is what its own colour tokens key off.
const { currentTheme, setTheme } = useTheme()

const choices = [
  { value: 'light', label: 'Light', icon: LucideSun },
  { value: 'dark', label: 'Dark', icon: LucideMoon },
  { value: 'system', label: 'System', icon: LucideMonitor },
]

const active = computed(
  () => choices.find((c) => c.value === currentTheme.value) || choices[0],
)
const label = computed(() => active.value.label)
const activeIcon = computed(() => active.value.icon)

const options = computed(() =>
  choices.map((choice) => ({
    label: choice.label,
    icon: currentTheme.value === choice.value ? LucideCheck : choice.icon,
    onClick: () => setTheme(choice.value),
  })),
)
</script>
