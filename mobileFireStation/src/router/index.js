import { createRouter, createWebHistory } from '@ionic/vue-router'
import LoginPage from '../pages/LoginPage.vue'
import { useTripStore } from '../stores/trip'
import { useAuthStore } from '../stores/auth'

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
  },
  {
    path: '/waybill/:id/start',
    component: () => import('../pages/WaybillTripStartPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/waybill/:id/view',
    component: () => import('../pages/WaybillDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/trip/active',
    component: () => import('../pages/ActiveTripPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/trip-end',
    component: () => import('../pages/TripEndPage.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard для проверки активной поездки
router.beforeEach(async (to, from, next) => {
  const tripStore = useTripStore()
  
  // Если переходим на путевые листы или другую страницу
  // и у нас есть активная поездка - перенаправляем на активную поездку
  if (to.path !== '/login' && !to.path.startsWith('/trip')) {
    // Загружаем данные поездки из localStorage если ещё не загружены
    if (!tripStore.hasActiveTrip) {
      const savedTrip = await tripStore.loadTripFromStorage()
      if (savedTrip) {
        // Проверяем валидность поездки
        if (savedTrip.number && savedTrip.car_number) {
          console.log('[Router] Valid active trip found, redirecting to /trip/active')
          return next('/trip/active')
        } else {
          // Невалидная поездка - очищаем
          console.warn('[Router] Invalid trip detected, clearing it')
          await tripStore.clearActiveTrip()
        }
      }
    }
  }
  
  next()
})

export default router
