<template>
  <PageHeader title="Reports">
    <template #actions>
      <Button
        v-if="result"
        label="Export CSV"
        :icon-left="LucideDownload"
        @click="exportCsv"
      />
      <Button
        v-if="active"
        label="Run"
        variant="solid"
        theme="blue"
        :icon-left="LucidePlay"
        :loading="running"
        @click="run"
      />
    </template>
  </PageHeader>

  <!-- Category tabs -->
  <div class="flex gap-1 overflow-x-auto border-b border-outline-gray-1 px-4 sm:px-5">
    <button
      v-for="c in categories"
      :key="c"
      type="button"
      class="whitespace-nowrap border-b-2 px-3 py-2.5 text-sm font-medium transition-colors"
      :class="c === category
        ? 'border-navy-500 text-navy-500'
        : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
      @click="category = c"
    >
      {{ c }}
      <span class="ml-1 text-xs text-ink-gray-4">{{ countIn(c) }}</span>
    </button>
  </div>

  <div class="flex-1 overflow-y-auto p-4 sm:p-5">
    <ErrorMessage class="mb-4" :message="catalogue.error || error" />

    <!-- Report picker for the active category -->
    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="r in inCategory"
        :key="r.name"
        type="button"
        class="rounded-lg border p-3 text-left transition-colors"
        :class="active?.name === r.name
          ? 'border-navy-300 bg-navy-50'
          : 'border-outline-gray-1 bg-surface-white hover:border-outline-gray-3'"
        @click="select(r)"
      >
        <p class="font-medium text-ink-gray-9">{{ r.name }}</p>
        <p class="mt-1 text-xs text-ink-gray-5">{{ r.description }}</p>
      </button>
    </div>

    <p v-if="!inCategory.length && !catalogue.loading" class="mt-4 text-sm text-ink-gray-5">
      No reports available in this category.
    </p>

    <!-- Filters + results -->
    <template v-if="active">
      <div class="mt-5 rounded-lg border border-outline-gray-1 p-3">
        <h2 class="mb-3 text-sm font-semibold text-ink-gray-8">{{ active.name }} filters</h2>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="f in active.filters" :key="f.fieldname">
            <label class="mb-1 block text-sm text-ink-gray-6">{{ f.label }}</label>

            <input
              v-if="f.type === 'date'"
              v-model="filters[f.fieldname]"
              type="date"
              class="ihotel-input"
            />
            <input
              v-else-if="f.type === 'number'"
              v-model="filters[f.fieldname]"
              type="number"
              class="ihotel-input"
            />
            <select
              v-else-if="f.type === 'select'"
              v-model="filters[f.fieldname]"
              class="ihotel-input"
            >
              <option value="">All</option>
              <option v-for="o in f.options" :key="o" :value="o">{{ o }}</option>
            </select>
            <!-- Link filters accept a typed value; the desk list is the source of truth. -->
            <input
              v-else
              v-model="filters[f.fieldname]"
              type="text"
              :placeholder="`Any ${f.label.toLowerCase()}`"
              class="ihotel-input"
            />
          </div>
        </div>
      </div>

      <div v-if="result" class="mt-4">
        <div class="mb-2 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-ink-gray-8">
            Results <span class="text-ink-gray-5">({{ result.rows.length }})</span>
          </h2>
        </div>

        <div v-if="!result.rows.length" class="rounded-lg border border-outline-gray-1 p-8 text-center text-sm text-ink-gray-6">
          No rows for these filters.
        </div>

        <!-- Wide report tables scroll inside their own container. -->
        <div v-else class="overflow-x-auto rounded-lg border border-outline-gray-1">
          <table class="min-w-full text-sm">
            <thead class="bg-surface-gray-1">
              <tr>
                <th
                  v-for="c in result.columns"
                  :key="c.fieldname"
                  class="whitespace-nowrap px-3 py-2 text-left font-medium text-ink-gray-6"
                  :class="isNumeric(c) && 'text-right'"
                >
                  {{ c.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, i) in result.rows"
                :key="i"
                class="border-t border-outline-gray-1 hover:bg-surface-gray-1"
              >
                <td
                  v-for="c in result.columns"
                  :key="c.fieldname"
                  class="whitespace-nowrap px-3 py-1.5"
                  :class="isNumeric(c) ? 'text-right tabular-nums text-ink-gray-8' : 'text-ink-gray-8'"
                >
                  <StatusBadge v-if="isStatus(c)" :value="row[c.fieldname]" />
                  <span v-else>{{ cell(row[c.fieldname], c) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Button, ErrorMessage, createResource } from 'frappe-ui'
import LucidePlay from '~icons/lucide/play'
import LucideDownload from '~icons/lucide/download'
import PageHeader from '@/components/PageHeader.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { currency, number, date as fmtDate } from '@/data/format'
import { downloadCsv, stamp } from '@/data/download'

const catalogue = createResource({
  url: 'ihotel.reports_api.get_reports',
  cache: 'ihotel-reports',
  auto: true,
})

const reports = computed(() => catalogue.data?.reports || [])
const categories = computed(() => catalogue.data?.categories || [])
const category = ref('')

// Land on the first category once the catalogue arrives.
watch(categories, (list) => {
  if (!category.value && list.length) category.value = list[0]
})

const inCategory = computed(() => reports.value.filter((r) => r.category === category.value))
const countIn = (c) => reports.value.filter((r) => r.category === c).length

const active = ref(null)
const filters = reactive({})
const result = ref(null)
const running = ref(false)
const error = ref('')

function select(report) {
  active.value = report
  result.value = null
  error.value = ''
  // Reset filters to this report's defaults.
  Object.keys(filters).forEach((k) => delete filters[k])
  for (const f of report.filters || []) filters[f.fieldname] = f.default ?? ''
}

// Switching category clears the open report so the two never disagree.
watch(category, () => {
  active.value = null
  result.value = null
})

async function run() {
  if (!active.value) return
  running.value = true
  error.value = ''
  try {
    result.value = await createResource({ url: 'ihotel.reports_api.run_report' }).submit({
      report_name: active.value.name,
      filters: JSON.stringify({ ...filters }),
    })
  } catch (e) {
    error.value = e?.messages?.[0] || e?.message || 'Could not run this report.'
    result.value = null
  } finally {
    running.value = false
  }
}

const NUMERIC = new Set(['Int', 'Float', 'Currency', 'Percent'])
const isNumeric = (c) => NUMERIC.has(c.fieldtype)
const isStatus = (c) => /status|priority/i.test(c.fieldname || '')

function cell(value, column) {
  if (value === null || value === undefined || value === '') return '—'
  if (column.fieldtype === 'Currency') return currency(value)
  if (column.fieldtype === 'Percent') return `${number(value, 1)}%`
  if (column.fieldtype === 'Float') return number(value, 2)
  if (column.fieldtype === 'Int') return number(value, 0)
  if (column.fieldtype === 'Date') return fmtDate(value)
  return value
}

function exportCsv() {
  if (!result.value) return
  const columns = result.value.columns.map((c) => ({
    label: c.label,
    value: (row) => row[c.fieldname] ?? '',
  }))
  const slug = active.value.name.toLowerCase().replace(/\s+/g, '-')
  downloadCsv(`${slug}-${stamp()}.csv`, columns, result.value.rows)
}
</script>

<style scoped>
.ihotel-input {
  width: 100%;
  border-radius: 0.375rem;
  border: 1px solid var(--outline-gray-2, #d1d5db);
  background: var(--surface-white, #fff);
  padding: 0.375rem 0.5rem;
  font-size: 0.875rem;
  color: var(--ink-gray-8, #1f272e);
}
</style>
