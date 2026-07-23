<template>
  <!-- Phones get cards: a wide table can only be read by scrolling sideways,
       which hides data rather than showing it. -->
  <div class="space-y-2 md:hidden">
    <p
      v-if="!rows.length"
      class="rounded-lg border border-outline-gray-1 p-6 text-center text-sm text-ink-gray-6"
    >
      {{ emptyState.title }}
    </p>
    <component
      :is="interactive ? 'button' : 'div'"
      v-for="row in rows"
      :key="row[rowKey]"
      class="block w-full rounded-lg border border-outline-gray-1 p-3 text-left"
      :class="interactive && 'transition-colors hover:border-outline-gray-2 active:bg-surface-gray-2'"
      @click="select(row)"
    >
      <slot name="card" :row="row" />
    </component>
  </div>

  <!-- md and up: the real table, sized to the container and set tighter than
       frappe-ui's default so more rows fit on screen. -->
  <div class="kel-list hidden rounded-lg border border-outline-gray-1 md:block">
    <ListView
      :columns="columns"
      :rows="rows"
      :row-key="rowKey"
      :options="{
        selectable: false,
        showTooltip: true,
        rowHeight: 36,
        getRowRoute,
        onRowClick,
        emptyState,
      }"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ListView } from 'frappe-ui'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  rowKey: { type: String, default: 'name' },
  getRowRoute: { type: Function, default: null },
  onRowClick: { type: Function, default: null },
  emptyState: {
    type: Object,
    default: () => ({ title: 'Nothing here yet', description: '' }),
  },
})

const router = useRouter()

const interactive = computed(() => Boolean(props.onRowClick || props.getRowRoute))

function select(row) {
  if (props.onRowClick) props.onRowClick(row)
  else if (props.getRowRoute) router.push(props.getRowRoute(row))
}
</script>
