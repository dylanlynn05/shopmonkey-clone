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
            <th>Customer</th>
            <th>Status</th>
            <th>Total</th>
            <th>Due date</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.id">
            <td>#{{ inv.id }}</td>
            <td>WO #{{ inv.work_order }}</td>
            <td>{{ inv.work_order_detail?.vehicle_detail?.customer_name || '—' }}</td>
            <td><span :class="['badge', inv.status === 'paid' ? 'badge-completed' : 'badge-pending']">{{ inv.status }}</span></td>
            <td>{{ formatMoney(inv.total) }}</td>
            <td>{{ formatDate(inv.due_date) }}</td>
            <td>{{ formatDate(inv.created_at) }}</td>
          </tr>
          <tr v-if="invoices.length === 0 && !loading">
            <td colspan="7" style="text-align: center; color: var(--text-muted);">No invoices yet.</td>
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
  // Date-only strings ("2026-11-11") are parsed as UTC midnight, which shows as the previous day in US time zones.
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(val)
  const d = dateOnly ? new Date(+dateOnly[1], +dateOnly[2] - 1, +dateOnly[3]) : new Date(val)
  return d.toLocaleDateString()
}

function formatMoney(val) {
  const n = Number(val)
  if (Number.isNaN(n)) return '—'
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(n)
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
