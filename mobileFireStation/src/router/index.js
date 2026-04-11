import { createRouter, createWebHistory } from '@ionic/vue-router'
import LoginPage from '../pages/LoginPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/waybills'
  },
  {
    path: '/login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/waybills',
    component: () => import('../pages/WaybillListPage.vue'),
    meta: { requiresAuth: true }
  },
 
  {
    path: '/settings',
    component: () => import('../pages/SettingsPage.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
