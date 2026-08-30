<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Vehicles</h1>
      <button class="btn btn-primary" @click="showForm = true">Add vehicle</button>
    </div>
    <div class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Year</th>
            <th>Make / Model</th>
            <th>VIN</th>
            <th>Customer</th>
            <th>License</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in vehicles" :key="v.id">
            <td>{{ v.year }}</td>
            <td>{{ v.make }} {{ v.model }}</td>
            <td>{{ v.vin || '—' }}</td>
            <td>{{ v.customer_name || '—' }}</td>
            <td>{{ v.license_plate || '—' }}</td>
          </tr>
          <tr v-if="vehicles.length === 0 && !loading">
            <td colspan="5" style="text-align: center; color: var(--text-muted);">No vehicles yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="card modal">
        <h2 style="margin-bottom: 1rem;">New vehicle</h2>
        <form @submit.prevent="createVehicle">
          <div class="form-group">
            <label>Customer</label>
            <select v-model="form.customer" required>
              <option value="">Select customer</option>
              <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.last_name }}, {{ c.first_name }}</option>
            </select>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Year</label>
              <input v-model.number="form.year" type="number" min="1900" max="2030" required />
            </div>
            <div class="form-group">
              <label>Make</label>
              <input v-model="form.make" required />
            </div>
          </div>
          <div class="form-group">
            <label>Model</label>
            <input v-model="form.model" required />
          </div>
          <div class="form-group">
            <label>VIN</label>
            <input v-model="form.vin" maxlength="17" />
          </div>
          <div class="form-group">
            <label>License plate</label>
            <input v-model="form.license_plate" />
          </div>
          <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
          <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
            <button type="submit" class="btn btn-primary">Save</button>
            <button type="button" class="btn btn-secondary" @click="showForm = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const vehicles = ref([])
const customers = ref([])
const loading = ref(false)
const showForm = ref(false)
const errorMessage = ref('')
const form = ref({
  customer: '',
  year: new Date().getFullYear(),
  make: '',
  model: '',
  vin: '',
  license_plate: '',
  color: '',
  mileage: null,
  notes: '',
})

async function fetchVehicles() {
  loading.value = true
  try {
    const { data } = await api.get('/api/vehicles/')
    vehicles.value = data.results ?? data
  } catch {
    vehicles.value = []
  } finally {
    loading.value = false
  }
}

async function fetchCustomers() {
  try {
    const { data } = await api.get('/api/customers/')
    customers.value = data.results ?? data
  } catch {
    customers.value = []
  }
}

async function createVehicle() {
  errorMessage.value = ''
  try {
    const payload = {
      customer: Number(form.value.customer),
      year: Number(form.value.year),
      make: form.value.make?.trim() || '',
      model: form.value.model?.trim() || '',
      vin: form.value.vin?.trim() || '',
      license_plate: form.value.license_plate?.trim() || '',
      color: form.value.color?.trim() || '',
      notes: form.value.notes?.trim() || '',
    }
    if (form.value.mileage != null && form.value.mileage !== '') {
      payload.mileage = Number(form.value.mileage)
    }
    await api.post('/api/vehicles/', payload)
    showForm.value = false
    form.value = { customer: '', year: new Date().getFullYear(), make: '', model: '', vin: '', license_plate: '', color: '', mileage: null, notes: '' }
    fetchVehicles()
  } catch (e) {
    const msg = e.response?.data
    errorMessage.value = typeof msg === 'object' ? JSON.stringify(msg) : (msg || e.message || 'Failed to add vehicle')
  }
}

onMounted(() => {
  fetchVehicles()
  fetchCustomers()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 2rem;
}
.modal {
  max-width: 420px;
  width: 100%;
}
.error-msg {
  color: var(--danger);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>
