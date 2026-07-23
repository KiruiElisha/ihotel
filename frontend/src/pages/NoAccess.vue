<template>
  <div class="flex h-full flex-col items-center justify-center gap-3 p-8 text-center">
    <LucideLock class="size-8 text-ink-gray-5" />
    <h1 class="text-lg font-medium text-ink-gray-9">No access</h1>
    <p class="max-w-md text-base text-ink-gray-5">
      You are signed in as <span class="font-medium">{{ session.user }}</span
      >, but your account does not have a hotel role. Ask an administrator to grant you access.
    </p>
    <Button label="Log out" @click="logout" />
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import LucideLock from '~icons/lucide/lock'
import { logout, session } from '@/data/session'
</script>
