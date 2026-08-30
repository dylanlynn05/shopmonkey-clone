<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">Repair Shop</div>
      <nav class="nav">
        <router-link to="/" class="nav-link" active-class="active">Dashboard</router-link>
        <router-link to="/customers" class="nav-link" active-class="active">Customers</router-link>
        <router-link to="/technicians" class="nav-link" active-class="active">Technicians</router-link>
        <router-link to="/vehicles" class="nav-link" active-class="active">Vehicles</router-link>
        <router-link to="/work-orders" class="nav-link" active-class="active">Work Orders</router-link>
        <router-link to="/estimates" class="nav-link" active-class="active">Estimates</router-link>
        <router-link to="/invoices" class="nav-link" active-class="active">Invoices</router-link>
      </nav>
      <div class="sidebar-footer">
        <button v-if="auth.isAuthenticated" class="btn btn-secondary" @click="logout">Log out</button>
      </div>
    </aside>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 240px;
  background: var(--bg-elevated);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.25rem 0;
}
.brand {
  font-size: 1.25rem;
  font-weight: 700;
  padding: 0 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
  color: var(--text);
}
.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.nav-link {
  padding: 0.6rem 1.25rem;
  color: var(--text-muted);
  transition: background 0.15s, color 0.15s;
  text-decoration: none;
}
.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text);
  text-decoration: none;
}
.nav-link.active {
  background: var(--bg-hover);
  color: var(--accent);
  font-weight: 500;
  border-right: 3px solid var(--accent);
}
.sidebar-footer {
  padding: 1rem 1.25rem 0;
  border-top: 1px solid var(--border);
}
.main {
  flex: 1;
  padding: 2rem;
  overflow-x: hidden;
}
</style>
