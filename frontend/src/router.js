import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('./views/Login.vue') },
  { path: '/', name: 'Layout', component: () => import('./views/Layout.vue'), redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('./views/Dashboard.vue') },
      { path: 'contracts', name: 'Contracts', component: () => import('./views/Contracts.vue') },
      { path: 'contracts/:id', name: 'ContractDetail', component: () => import('./views/ContractDetail.vue') },
      { path: 'invoices', name: 'Invoices', component: () => import('./views/Invoices.vue') },
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
