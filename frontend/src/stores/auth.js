import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isReady = computed(() => initialized.value)

  function setToken(newToken) {
    token.value = newToken
    if (newToken) localStorage.setItem('token', newToken)
    else localStorage.removeItem('token')
  }

  async function init() {
    if (initialized.value) return
    if (token.value) {
      try {
        api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
        // Optional: validate token with a lightweight request
      } catch {
        setToken(null)
      }
    }
    initialized.value = true
  }

  async function login(username, password) {
    const { data } = await api.post('/api/auth/token/', { username, password })
    setToken(data.access)
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
    return data
  }

  function logout() {
    setToken(null)
    delete api.defaults.headers.common['Authorization']
  }

  return {
    token,
    isAuthenticated,
    isReady,
    init,
    login,
    logout,
    setToken,
  }
})
