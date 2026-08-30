<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">New work order</h1>
      <router-link to="/work-orders" class="btn btn-secondary">Back to list</router-link>
    </div>
    <div class="card" style="max-width: 480px;">
      <form @submit.prevent="create">
        <div class="form-group">
          <label>Vehicle</label>
          <select v-model="form.vehicle" required>
            <option value="">Select vehicle</option>
            <option v-for="v in vehicles" :key="v.id" :value="v.id">
              {{ v.year }} {{ v.make }} {{ v.model }} – {{ v.customer_name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Priority</label>
          <select v-model.number="form.priority" required>
            <option :value="4">Urgent</option>
            <option :value="3">High</option>
            <option :value="2">Normal</option>
            <option :value="1">Low</option>
          </select>
        </div>
        <div class="form-group">
          <label>Technician</label>
          <select v-model="form.assigned_technician">
            <option value="">TBD</option>
            <option v-for="t in technicians" :key="t.id" :value="t.id">{{ t.first_name }} {{ t.last_name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" rows="3"></textarea>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label>Rate ($/hr)</label>
            <input v-model.number="form.rate" type="number" min="0" step="0.01" />
          </div>
          <div class="form-group">
            <label>Estimated time (hours)</label>
            <input v-model.number="form.estimated_time_hours" type="number" min="0" step="0.25" />
          </div>
        </div>
        <div class="form-group">
          <label>Total labor</label>
          <div class="total-labor" aria-readonly="true">{{ formatMoney(formTotalPrice) }}</div>
        </div>
        <div class="form-group">
          <label>Scheduled date</label>
          <input v-model="form.scheduled_date" type="date" />
        </div>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
          <button type="submit" class="btn btn-primary" :disabled="saving">Create work order</button>
          <router-link to="/work-orders" class="btn btn-secondary">Cancel</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const vehicles = ref([])
const technicians = ref([])
const saving = ref(false)
const form = ref({
  vehicle: '',
  priority: 2,
  assigned_technician: '',
  description: '',
  rate: 0,
  estimated_time_hours: 0,
  scheduled_date: '',
  status: 'waiting_customer_approval',
})

function formatMoney(val) {
  const n = Number(val)
  if (Number.isNaN(n)) return '$0.00'
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(n)
}

const formTotalPrice = computed(() => {
  const r = Number(form.value.rate) || 0
  const h = Number(form.value.estimated_time_hours) || 0
  return r * h
})

onMounted(async () => {
  try {
    const [vRes, tRes] = await Promise.all([
      api.get('/api/vehicles/'),
      api.get('/api/technicians/'),
    ])
    vehicles.value = vRes.data.results ?? vRes.data ?? []
    technicians.value = tRes.data.results ?? tRes.data ?? []
  } catch (e) {
    console.error(e)
  }
})

async function create() {
  saving.value = true
  try {
    const payload = {
      vehicle: Number(form.value.vehicle),
      priority: Number(form.value.priority),
      description: form.value.description,
      rate: Number(form.value.rate || 0),
      estimated_time_hours: Number(form.value.estimated_time_hours || 0),
      scheduled_date: form.value.scheduled_date || null,
      status: 'waiting_customer_approval',
    }
    if (form.value.assigned_technician) {
      payload.assigned_technician = Number(form.value.assigned_technician)
    }
    const { data } = await api.post('/api/work-orders/', payload)
    router.push({ name: 'WorkOrders' })
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.total-labor {
  font-weight: 600;
  font-size: 1rem;
}
</style>
