<template>
  <div class="login-page">
    <div class="login-card card">
      <h1 class="login-title">Repair Shop Manager</h1>
      <p class="login-subtitle">Sign in to continue</p>
      <form @submit.prevent="submit" class="login-form">
        <div class="form-group">
          <label>Username</label>
          <input v-model="username" type="text" required autocomplete="username" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input v-model="password" type="password" required autocomplete="current-password" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn btn-primary" :disabled="loading">Sign in</button>
      </form>
      <p class="demo-hint">
        Use a Django superuser account. Run: <code>python manage.py createsuperuser</code>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Invalid username or password.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.login-card {
  width: 100%;
  max-width: 400px;
}
.login-title {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}
.login-subtitle {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}
.login-form {
  margin-bottom: 1rem;
}
.login-form .btn {
  width: 100%;
  margin-top: 0.5rem;
}
.error {
  color: var(--danger);
  font-size: 0.9rem;
  margin: 0.5rem 0;
}
.demo-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 1rem;
}
.demo-hint code {
  background: var(--bg);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}
</style>
