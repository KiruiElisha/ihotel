<template>
  <header
    class="flex min-h-14 shrink-0 flex-wrap items-center justify-between gap-2 border-b border-outline-gray-1 px-3 py-2 sm:px-5"
  >
    <div class="flex min-w-0 items-center gap-1.5">
      <!-- The sidebar is an off-canvas drawer below md, so it needs a trigger. -->
      <Button
        class="md:hidden"
        variant="ghost"
        label="Open menu"
        :icon="LucideMenu"
        @click="openDrawer"
      />
      <Breadcrumbs :items="items" />
    </div>
    <div class="flex items-center gap-2">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
import { computed, inject } from 'vue'
import { Breadcrumbs, Button } from 'frappe-ui'
import LucideMenu from '~icons/lucide/menu'

const props = defineProps({
  title: { type: String, required: true },
  parent: { type: Object, default: null },
})

// Provided by AppShell; a no-op if this header is ever used outside it.
const openDrawer = inject('openDrawer', () => {})

const items = computed(() =>
  props.parent ? [props.parent, { label: props.title }] : [{ label: props.title }],
)
</script>
