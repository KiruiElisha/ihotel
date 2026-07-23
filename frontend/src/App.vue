<template>
  <FrappeUIProvider>
    <div class="h-full">
      <AppShell v-if="isReady">
        <router-view />
      </AppShell>
      <div v-else class="flex h-full items-center justify-center">
        <LoadingIndicator class="size-6 text-ink-gray-6" />
      </div>
      <Dialogs />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { Dialogs, FrappeUIProvider, LoadingIndicator } from 'frappe-ui'
import AppShell from '@/components/AppShell.vue'
import { isReady } from '@/data/session'
</script>
