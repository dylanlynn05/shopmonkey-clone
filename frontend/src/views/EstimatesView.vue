<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Estimates</h1>
    </div>
    <div class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Work order</th>
            <th>Version</th>
            <th>Lines</th>
            <th>Total</th>
            <th>Approved</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in estimates" :key="e.id">
            <td>#{{ e.id }}</td>
            <td>WO #{{ e.work_order }}</td>
            <td>v{{ e.version }}</td>
            <td>{{ e.line_items.length }}</td>
            <td>{{ formatMoney(e.total) }}</td>
            <td>{{ e.approved_at ? formatDate(e.approved_at) : '—' }}</td>
            <td>{{ formatDate(e.created_at) }}</td>
          </tr>
          <tr v-if="estimates.length === 0 && !loading">
            <td colspan="7" style="text-align: center; color: var(--text-muted);">No estimates yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const estimates = ref([])
const loading = ref(false)

function formatDate(val) {
  if (!val) return '—'
  return new Date(val).toLocaleDateString()
}

function formatMoney(val) {
  const n = Number(val)
  if (Number.isNaN(n)) return '—'
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(n)
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/api/estimates/')
    estimates.value = data.results ?? data
  } catch {
    estimates.value = []
  } finally {
    loading.value = false
  }
})
</script>
