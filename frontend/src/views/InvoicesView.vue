<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Invoices</h1>
    </div>
    <div class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Work order</th>
            <th>Status</th>
            <th>Due date</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.id">
            <td>#{{ inv.id }}</td>
            <td>WO #{{ inv.work_order }}</td>
            <td><span :class="['badge', inv.status === 'paid' ? 'badge-completed' : 'badge-pending']">{{ inv.status }}</span></td>
            <td>{{ formatDate(inv.due_date) }}</td>
            <td>{{ formatDate(inv.created_at) }}</td>
          </tr>
          <tr v-if="invoices.length === 0 && !loading">
            <td colspan="5" style="text-align: center; color: var(--text-muted);">No invoices yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const invoices = ref([])
const loading = ref(false)

function formatDate(val) {
  if (!val) return '—'
  return new Date(val).toLocaleDateString()
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/api/invoices/')
    invoices.value = data.results ?? data
  } catch {
    invoices.value = []
  } finally {
    loading.value = false
  }
})
</script>
