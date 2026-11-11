<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
    </div>
    <p v-if="error" class="error-msg">{{ error }}</p>
    <div class="dashboard-grid">
      <div class="card stat-card">
        <div class="stat-value">{{ stats.open_work_orders }}</div>
        <div class="stat-label">Open work orders</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value stat-urgent">{{ stats.urgent_open_work_orders }}</div>
        <div class="stat-label">Urgent &amp; open</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ stats.customers }}</div>
        <div class="stat-label">Customers</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ stats.vehicles }}</div>
        <div class="stat-label">Vehicles</div>
      </div>
    </div>
    <div class="card" style="margin-top: 1.5rem;">
      <h2 class="section-title">Work orders by status</h2>
      <div class="status-grid">
        <router-link
          v-for="s in STATUSES"
          :key="s.value"
          :to="{ name: 'WorkOrders' }"
          class="status-tile"
        >
          <span :class="['badge', s.badge]">{{ s.label }}</span>
          <span class="status-count">{{ stats.work_orders_by_status[s.value] ?? 0 }}</span>
        </router-link>
      </div>
    </div>
    <div class="card" style="margin-top: 1.5rem;">
      <h2 class="section-title">Quick actions</h2>
      <div class="quick-actions">
        <router-link to="/work-orders/new" class="btn btn-primary">New work order</router-link>
        <router-link to="/customers" class="btn btn-secondary">Add customer</router-link>
        <router-link to="/vehicles" class="btn btn-secondary">Add vehicle</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const STATUSES = [
  { value: 'waiting_customer_approval', label: 'Waiting on customer approval', badge: 'badge-pending' },
  { value: 'waiting_parts', label: 'Waiting on parts', badge: 'badge-warning' },
  { value: 'in_progress', label: 'In progress', badge: 'badge-progress' },
  { value: 'ready_pickup', label: 'Ready for pickup', badge: 'badge-info' },
  { value: 'completed', label: 'Completed', badge: 'badge-completed' },
]

const error = ref('')
const stats = ref({
  open_work_orders: 0,
  urgent_open_work_orders: 0,
  customers: 0,
  vehicles: 0,
  work_orders_by_status: {},
})

onMounted(async () => {
  try {
    const { data } = await api.get('/api/work-orders/stats/')
    stats.value = data
  } catch {
    error.value = 'Could not load dashboard stats. Is the API running?'
  }
})
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}
.stat-card {
  text-align: center;
  padding: 1.5rem;
}
.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent);
}
.stat-urgent {
  color: var(--danger);
}
.stat-label {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}
.section-title {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
}
.status-tile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  text-decoration: none;
}
.status-tile:hover {
  background: var(--bg-hover);
  text-decoration: none;
}
.status-count {
  font-size: 1.25rem;
  font-weight: 700;
}
.quick-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.error-msg {
  color: var(--danger);
  margin-bottom: 1rem;
}
</style>
