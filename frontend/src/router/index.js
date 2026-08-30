import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'customers', name: 'Customers', component: () => import('../views/CustomersView.vue') },
      { path: 'technicians', name: 'Technicians', component: () => import('../views/TechniciansView.vue') },
      { path: 'vehicles', name: 'Vehicles', component: () => import('../views/VehiclesView.vue') },
      { path: 'work-orders', name: 'WorkOrders', component: () => import('../views/WorkOrdersView.vue') },
      { path: 'work-orders/new', name: 'NewWorkOrder', component: () => import('../views/NewWorkOrderView.vue') },
      { path: 'estimates', name: 'Estimates', component: () => import('../views/EstimatesView.vue') },
      { path: 'invoices', name: 'Invoices', component: () => import('../views/InvoicesView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const { useAuthStore } = await import('../stores/auth')
  const authStore = useAuthStore()
  await authStore.init()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
