<template>
  <div class="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
onMounted(() => useAuthStore().init())
</script>

<style scoped>
.app {
  min-height: 100vh;
}
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  font-size: 1.25rem;
  color: var(--text-muted);
}
</style>
