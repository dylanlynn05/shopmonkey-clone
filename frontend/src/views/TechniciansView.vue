<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Technicians</h1>
      <button class="btn btn-primary" @click="openCreateForm">Add technician</button>
    </div>

    <div class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Level</th>
            <th>Date started</th>
            <th>Status</th>
            <th style="width: 140px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in technicians" :key="t.id">
            <td>{{ t.last_name }}, {{ t.first_name }}</td>
            <td>{{ t.phone || '—' }}</td>
            <td>{{ t.email || '—' }}</td>
            <td>{{ formatLevel(t.level) }}</td>
            <td>{{ t.date_started }}</td>
            <td>
              <span :class="['status-pill', t.is_active ? 'status-active' : 'status-inactive']">
                {{ t.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button class="btn btn-secondary btn-sm" @click="openEditForm(t)">Edit</button>
                <button class="btn btn-danger btn-sm" @click="confirmDelete(t)">Delete</button>
              </div>
            </td>
          </tr>
          <tr v-if="technicians.length === 0 && !loading">
            <td colspan="5" style="text-align: center; color: var(--text-muted);">
              No technicians yet.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="card modal">
        <h2 style="margin-bottom: 1rem;">
          {{ editingTechnician ? 'Edit technician' : 'New technician' }}
        </h2>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>First name</label>
            <input v-model="form.first_name" required />
          </div>
          <div class="form-group">
            <label>Last name</label>
            <input v-model="form.last_name" required />
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input v-model="form.phone" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" />
          </div>
          <div class="form-group">
            <label>Tech level</label>
            <select v-model="form.level" required>
              <option disabled value="">Select level</option>
              <option value="A">A Tech</option>
              <option value="B">B Tech</option>
              <option value="C">C Tech</option>
            </select>
          </div>
          <div class="form-group">
            <label>Date started</label>
            <input v-model="form.date_started" type="date" required />
          </div>
          <div class="form-group checkbox-row">
            <label>
              <input v-model="form.is_active" type="checkbox" />
              Active
            </label>
          </div>
          <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">
              {{ editingTechnician ? 'Save changes' : 'Save' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="closeForm">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="card modal">
        <h2 style="margin-bottom: 0.75rem;">Delete technician</h2>
        <p style="margin-bottom: 1rem;">
          Are you sure you want to delete
          <strong>{{ deleteTarget.last_name }}, {{ deleteTarget.first_name }}</strong>?
        </p>
        <p class="warning-text">
          This action cannot be undone.
        </p>
        <div class="form-actions">
          <button class="btn btn-danger" @click="deleteTechnician">Delete</button>
          <button class="btn btn-secondary" @click="deleteTarget = null">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const technicians = ref([])
const loading = ref(false)
const showForm = ref(false)
const editingTechnician = ref(null)
const deleteTarget = ref(null)
const errorMessage = ref('')

// toISOString() is UTC, so in the evening (US time) it would return tomorrow's date.
function todayLocal() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const emptyForm = () => ({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  level: 'C',
  date_started: todayLocal(),
  is_active: true,
})

const form = ref(emptyForm())

async function fetchTechnicians() {
  loading.value = true
  try {
    const { data } = await api.get('/api/technicians/')
    technicians.value = data.results ?? data
  } catch (e) {
    console.error(e)
    technicians.value = []
  } finally {
    loading.value = false
  }
}

function openCreateForm() {
  editingTechnician.value = null
  form.value = emptyForm()
  errorMessage.value = ''
  showForm.value = true
}

function openEditForm(technician) {
  editingTechnician.value = technician
  form.value = {
    first_name: technician.first_name,
    last_name: technician.last_name,
    email: technician.email || '',
    phone: technician.phone || '',
    level: technician.level || 'C',
    date_started: technician.date_started || todayLocal(),
    is_active: technician.is_active,
  }
  errorMessage.value = ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingTechnician.value = null
  errorMessage.value = ''
}

async function submitForm() {
  errorMessage.value = ''
  const payload = {
    first_name: form.value.first_name?.trim() || '',
    last_name: form.value.last_name?.trim() || '',
    email: form.value.email?.trim() || '',
    phone: form.value.phone?.trim() || '',
    level: form.value.level,
    date_started: form.value.date_started,
    is_active: !!form.value.is_active,
  }

  try {
    if (editingTechnician.value) {
      await api.put(`/api/technicians/${editingTechnician.value.id}/`, payload)
    } else {
      await api.post('/api/technicians/', payload)
    }
    closeForm()
    await fetchTechnicians()
  } catch (e) {
    const msg = e.response?.data
    errorMessage.value =
      typeof msg === 'object' ? JSON.stringify(msg) : (msg || e.message || 'Failed to save technician')
  }
}

function confirmDelete(technician) {
  deleteTarget.value = technician
}

async function deleteTechnician() {
  if (!deleteTarget.value) return
  try {
    await api.delete(`/api/technicians/${deleteTarget.value.id}/`)
    deleteTarget.value = null
    await fetchTechnicians()
  } catch (e) {
    console.error(e)
  }
}

function formatLevel(level) {
  if (level === 'A') return 'A Tech'
  if (level === 'B') return 'B Tech'
  if (level === 'C') return 'C Tech'
  return level || '—'
}

onMounted(fetchTechnicians)
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
.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
.error-msg {
  color: var(--danger);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
.actions {
  display: flex;
  gap: 0.35rem;
}
.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}
.btn-danger {
  background: var(--danger);
  border-color: var(--danger);
  color: #fff;
}
.btn-danger:hover {
  filter: brightness(0.95);
}
.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}
.status-active {
  background: rgba(46, 204, 113, 0.1);
  color: #27ae60;
}
.status-inactive {
  background: rgba(149, 165, 166, 0.15);
  color: #7f8c8d;
}
.checkbox-row label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
}
.warning-text {
  font-size: 0.9rem;
  color: var(--danger);
  margin-bottom: 1rem;
}
</style>

