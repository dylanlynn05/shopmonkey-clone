import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

const token = localStorage.getItem('token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

function clearSessionAndRedirect() {
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  delete api.defaults.headers.common['Authorization']
  if (!import.meta.env.SSR && window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

// Shared so that several requests failing at once trigger a single refresh call.
let refreshPromise = null

async function refreshAccessToken() {
  const refresh = localStorage.getItem('refreshToken')
  if (!refresh) throw new Error('No refresh token')
  const { data } = await axios.post(`${baseURL}/api/auth/token/refresh/`, { refresh })
  localStorage.setItem('token', data.access)
  if (data.refresh) localStorage.setItem('refreshToken', data.refresh)
  api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
  return data.access
}

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    const isAuthCall = original?.url?.includes('/api/auth/')
    if (err.response?.status === 401 && original && !original._retried && !isAuthCall) {
      original._retried = true
      try {
        refreshPromise = refreshPromise || refreshAccessToken()
        const access = await refreshPromise
        original.headers['Authorization'] = `Bearer ${access}`
        return api(original)
      } catch {
        clearSessionAndRedirect()
      } finally {
        refreshPromise = null
      }
    } else if (err.response?.status === 401 && !isAuthCall) {
      clearSessionAndRedirect()
    }
    return Promise.reject(err)
  }
)

export default api
