<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
    </div>
    <div class="dashboard-grid">
      <div class="card stat-card">
        <div class="stat-value">{{ stats.workOrdersPending }}</div>
        <div class="stat-label">Pending work orders</div>
      </div>
      <div class="card stat-card">
        <div class="stat-value">{{ stats.workOrdersInProgress }}</div>
        <div class="stat-label">In progress</div>
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
      <h2 style="margin-bottom: 1rem; font-size: 1.1rem;">Quick actions</h2>
      <div class="quick-actions">
        <router-link to="/work-orders" class="btn btn-primary">New work order</router-link>
        <router-link to="/customers" class="btn btn-secondary">Add customer</router-link>
        <router-link to="/vehicles" class="btn btn-secondary">Add vehicle</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref({
  workOrdersPending: 0,
  workOrdersInProgress: 0,
  customers: 0,
  vehicles: 0,
})

onMounted(async () => {
  try {
    const [woRes, custRes, vehRes] = await Promise.all([
      api.get('/api/work-orders/'),
      api.get('/api/customers/'),
      api.get('/api/vehicles/'),
    ])
    const orders = woRes.data.results || woRes.data || []
    stats.value.workOrdersPending = orders.filter((o) => o.status === 'pending').length
    stats.value.workOrdersInProgress = orders.filter((o) => o.status === 'in_progress').length
    const custList = custRes.data.results || custRes.data || []
    const vehList = vehRes.data.results || vehRes.data || []
    stats.value.customers = custList.length
    stats.value.vehicles = vehList.length
  } catch {
    // API may require auth or not be running
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
.stat-label {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}
.quick-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
</style>
