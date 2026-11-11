<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Customers</h1>
      <button class="btn btn-primary" @click="showForm = true">Add customer</button>
    </div>
    <input
      v-model="search"
      class="search-input"
      type="search"
      placeholder="Search by name, email, or phone"
      @input="onSearch"
    />
    <div class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in customers" :key="c.id">
            <td>{{ c.last_name }}, {{ c.first_name }}</td>
            <td>{{ c.phone }}</td>
            <td>{{ c.email || '—' }}</td>
            <td>
              <button class="btn btn-secondary" style="padding: 0.35rem 0.6rem; font-size: 0.875rem;">Edit</button>
            </td>
          </tr>
          <tr v-if="customers.length === 0 && !loading">
            <td colspan="4" style="text-align: center; color: var(--text-muted);">No customers yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="card modal">
        <h2 style="margin-bottom: 1rem;">New customer</h2>
        <form @submit.prevent="createCustomer">
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
            <input v-model="form.phone" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" />
          </div>
          <div class="form-group">
            <label>Address</label>
            <textarea v-model="form.address" rows="2"></textarea>
          </div>
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

const customers = ref([])
const loading = ref(false)
const showForm = ref(false)
const search = ref('')
let searchTimer = null
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  address: '',
  notes: '',
})

async function fetchCustomers() {
  loading.value = true
  try {
    const params = search.value.trim() ? { search: search.value.trim() } : {}
    const { data } = await api.get('/api/customers/', { params })
    customers.value = data.results ?? data
  } catch {
    customers.value = []
  } finally {
    loading.value = false
  }
}

async function createCustomer() {
  try {
    await api.post('/api/customers/', form.value)
    showForm.value = false
    form.value = { first_name: '', last_name: '', email: '', phone: '', address: '', notes: '' }
    fetchCustomers()
  } catch (e) {
    console.error(e)
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchCustomers, 250)
}

onMounted(fetchCustomers)
</script>

<style scoped>
.search-input {
  width: 100%;
  max-width: 360px;
  margin-bottom: 1rem;
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
  max-width: 420px;
  width: 100%;
}
</style>
