<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Work orders</h1>
      <router-link to="/work-orders/new" class="btn btn-primary">New work order</router-link>
    </div>
    <div v-if="workOrders.length > 0" class="wo-card-grid">
      <article
        v-for="wo in workOrders"
        :key="wo.id"
        class="card wo-card"
      >
        <div class="wo-card-main">
          <p class="wo-card-job">{{ jobTitle(wo) }}</p>
          <p class="wo-card-vehicle">{{ vehicleLabel(wo) }}</p>
          <p class="wo-card-customer">{{ customerLabel(wo) }}</p>
        </div>
        <div class="wo-card-meta">
          <span :class="['badge', priorityClass(wo.priority)]">{{ priorityLabel(wo.priority) }}</span>
          <span :class="['badge', statusClass(wo.status)]">{{ statusLabel(wo.status) }}</span>
          <span class="wo-card-meta-muted">WO #{{ wo.id }}</span>
          <span class="wo-card-meta-muted">{{ wo.technician_name || 'TBD' }}</span>
          <span class="wo-card-meta-muted">Scheduled {{ formatDate(wo.scheduled_date) }}</span>
          <span class="wo-card-meta-muted">{{ formatMoney(wo.rate) }}/hr · {{ wo.estimated_time_hours ?? '—' }}h · {{ formatMoney(wo.total_labor) }}</span>
          <span class="wo-card-meta-muted">Created {{ formatDate(wo.created_at) }}</span>
        </div>
        <div class="wo-card-actions">
          <button type="button" class="btn btn-secondary btn-sm" @click="openEdit(wo)">Edit</button>
        </div>
      </article>
    </div>
    <div v-else-if="!loading" class="card wo-empty">No work orders yet.</div>

    <div v-if="showEdit" class="modal-overlay" @click.self="closeEdit">
      <div class="card modal">
        <h2 style="margin-bottom: 1rem;">Edit work order</h2>
        <form @submit.prevent="saveEdit">
          <div class="form-group">
            <label>Status</label>
            <select v-model="editForm.status" required>
              <option value="waiting_customer_approval">Waiting on customer approval</option>
              <option value="waiting_parts">Waiting on parts</option>
              <option value="in_progress">In progress</option>
              <option value="ready_pickup">Ready for pickup</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="form-group">
            <label>Priority</label>
            <select v-model.number="editForm.priority" required>
              <option :value="4">Urgent</option>
              <option :value="3">High</option>
              <option :value="2">Normal</option>
              <option :value="1">Low</option>
            </select>
          </div>
          <div class="form-group">
            <label>Technician</label>
            <select v-model="editForm.assigned_technician">
              <option value="">TBD</option>
              <option v-for="t in technicians" :key="t.id" :value="t.id">{{ t.first_name }} {{ t.last_name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editForm.description" rows="3"></textarea>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Rate ($/hr)</label>
              <input v-model.number="editForm.rate" type="number" min="0" step="0.01" required />
            </div>
            <div class="form-group">
              <label>Estimated time (hours)</label>
              <input v-model.number="editForm.estimated_time_hours" type="number" min="0" step="0.25" required />
            </div>
          </div>
          <div class="form-group">
            <label>Total labor</label>
            <div class="total-labor" aria-readonly="true">{{ formatMoney(editFormTotalPrice) }}</div>
          </div>
          <div class="form-group">
            <label>Scheduled date</label>
            <input v-model="editForm.scheduled_date" type="date" />
          </div>
          <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="saving">Save</button>
            <button type="button" class="btn btn-secondary" @click="closeEdit">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const workOrders = ref([])
const loading = ref(false)
const technicians = ref([])
const showEdit = ref(false)
const saving = ref(false)
const editingId = ref(null)
const errorMessage = ref('')
const editForm = ref({
  status: 'waiting_customer_approval',
  priority: 2,
  assigned_technician: '',
  description: '',
  rate: 0,
  estimated_time_hours: 0,
  scheduled_date: '',
})

const editFormTotalPrice = computed(() => {
  const r = Number(editForm.value.rate) || 0
  const h = Number(editForm.value.estimated_time_hours) || 0
  return r * h
})

const STATUS_LABELS = {
  waiting_customer_approval: 'Waiting on customer approval',
  waiting_parts: 'Waiting on parts',
  in_progress: 'In progress',
  ready_pickup: 'Ready for pickup',
  completed: 'Completed',
}

const PRIORITY_LABELS = {
  4: 'Urgent',
  3: 'High',
  2: 'Normal',
  1: 'Low',
}

function statusClass(status) {
  const m = {
    waiting_customer_approval: 'badge-pending',
    waiting_parts: 'badge-warning',
    in_progress: 'badge-progress',
    ready_pickup: 'badge-info',
    completed: 'badge-completed',
  }
  return m[status] || 'badge-pending'
}

function statusLabel(status) {
  return STATUS_LABELS[status] || status || '—'
}

function priorityLabel(p) {
  const n = Number(p)
  return PRIORITY_LABELS[n] || 'Normal'
}

function priorityClass(p) {
  const n = Number(p)
  const m = {
    4: 'badge-priority-urgent',
    3: 'badge-priority-high',
    2: 'badge-priority-normal',
    1: 'badge-priority-low',
  }
  return m[n] || 'badge-priority-normal'
}

function jobTitle(wo) {
  const d = (wo.description || '').trim()
  return d || 'No job description yet'
}

function vehicleLabel(wo) {
  const v = wo.vehicle_detail
  if (!v) return '—'
  return [v.year, v.make, v.model].filter(Boolean).join(' ')
}

function customerLabel(wo) {
  return wo.vehicle_detail?.customer_name || '—'
}

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

async function fetch() {
  loading.value = true
  try {
    const { data } = await api.get('/api/work-orders/')
    const list = data.results ?? data
    workOrders.value = [...list].sort((a, b) => {
      const pa = Number(a.priority ?? 2)
      const pb = Number(b.priority ?? 2)
      if (pb !== pa) return pb - pa
      return new Date(b.created_at) - new Date(a.created_at)
    })
  } catch {
    workOrders.value = []
  } finally {
    loading.value = false
  }
}

async function fetchTechnicians() {
  try {
    const { data } = await api.get('/api/technicians/')
    technicians.value = data.results ?? data
  } catch {
    technicians.value = []
  }
}

function openEdit(wo) {
  editingId.value = wo.id
  errorMessage.value = ''
  editForm.value = {
    status: wo.status || 'waiting_customer_approval',
    priority: Number(wo.priority ?? 2),
    assigned_technician: wo.assigned_technician ?? '',
    description: wo.description || '',
    rate: Number(wo.rate || 0),
    estimated_time_hours: Number(wo.estimated_time_hours || 0),
    scheduled_date: wo.scheduled_date || '',
  }
  showEdit.value = true
}

function closeEdit() {
  showEdit.value = false
  editingId.value = null
  errorMessage.value = ''
}

async function saveEdit() {
  if (!editingId.value) return
  saving.value = true
  errorMessage.value = ''
  try {
    const payload = {
      status: editForm.value.status,
      priority: Number(editForm.value.priority),
      description: editForm.value.description,
      scheduled_date: editForm.value.scheduled_date || null,
      rate: Number(editForm.value.rate),
      estimated_time_hours: Number(editForm.value.estimated_time_hours),
      assigned_technician: editForm.value.assigned_technician ? Number(editForm.value.assigned_technician) : null,
    }
    await api.patch(`/api/work-orders/${editingId.value}/`, payload)
    closeEdit()
    await fetch()
  } catch (e) {
    const msg = e.response?.data
    errorMessage.value =
      typeof msg === 'object' ? JSON.stringify(msg) : (msg || e.message || 'Failed to update work order')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([fetch(), fetchTechnicians()])
})
</script>

<style scoped>
.wo-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}
.wo-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem 1.35rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.wo-card:hover {
  border-color: var(--bg-hover);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
}
.wo-card-main {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.wo-card-job {
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--text);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.wo-card-vehicle {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text);
  line-height: 1.4;
}
.wo-card-customer {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-muted);
  line-height: 1.4;
}
.wo-card-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  padding-top: 0.25rem;
  border-top: 1px solid var(--border);
}
.wo-card-meta-muted {
  color: var(--text-muted);
}
.wo-card-actions {
  display: flex;
  justify-content: flex-end;
}
.wo-empty {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem 1.25rem;
}
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
  max-width: 520px;
  width: 100%;
}
.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
.actions {
  display: flex;
  gap: 0.35rem;
}
.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}
.error-msg {
  color: var(--danger);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
.total-labor {
  font-weight: 600;
  font-size: 1rem;
}
.badge-priority-urgent {
  background: var(--danger);
  color: white;
}
.badge-priority-high {
  background: #c2410c;
  color: white;
}
.badge-priority-normal {
  background: var(--bg-hover);
  color: var(--text);
  border: 1px solid var(--border);
}
.badge-priority-low {
  background: transparent;
  color: var(--text-muted);
  border: 1px solid var(--border);
}
</style>
