import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { IonicVue } from '@ionic/vue'
import { addIcons } from 'ionicons'
import {
  documentOutline,
  playOutline,
  warningOutline,
  closeCircle,
  menu,
  arrowBack,
  add,
  close,
  settingsOutline,
  refreshOutline,
} from 'ionicons/icons'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

/* Core CSS required for Ionic components to work properly */
import '@ionic/vue/css/core.css'

/* Basic CSS for apps built with Ionic */
import '@ionic/vue/css/normalize.css'
import '@ionic/vue/css/structure.css'
import '@ionic/vue/css/typography.css'

/* Optional CSS utils that can be commented out */
import '@ionic/vue/css/padding.css'
import '@ionic/vue/css/float-elements.css'
import '@ionic/vue/css/text-alignment.css'
import '@ionic/vue/css/text-transformation.css'
import '@ionic/vue/css/flex-utils.css'
import '@ionic/vue/css/display.css'

import './style.css'

const app = createApp(App)

// Регистрируем иконки
addIcons({
  documentOutline,
  playOutline,
  warningOutline,
  closeCircle,
  menu,
  arrowBack,
  add,
  close,
  settingsOutline,
  refreshOutline,
})

const pinia = createPinia()
app.use(pinia)
app.use(IonicVue)

// Загружаем сохранённую авторизацию при запуске (после инициализации Pinia)
const authStore = useAuthStore()

// Регистрируем router
app.use(router)

// Защита маршрутов - проверяем авторизацию перед каждым переходом
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const isAuthenticated = !!auth.token && !!auth.user
  const requiresAuth = to.meta.requiresAuth !== false
  
  console.log(`[Router] Navigating to ${to.path}`, {
    isAuthenticated,
    hasToken: !!auth.token,
    hasUser: !!auth.user,
    requiresAuth,
  })
  
  if (to.path === '/login') {
    // Если уже авторизован, не показываем логин
    if (isAuthenticated) {
      console.log('[Router] User already authenticated, redirecting to waybills')
      next('/waybills')
    } else {
      next()
    }
  } else if (to.path === '/') {
    // Главная страница - редирект в зависимости от авторизации
    if (isAuthenticated) {
      next('/waybills')
    } else {
      next('/login')
    }
  } else if (requiresAuth && !isAuthenticated) {
    // Если нужна авторизация, но её нет - на логин
    console.log('[Router] User not authenticated, redirecting to login', { to: to.path })
    next('/login')
  } else if (requiresAuth && !auth.user) {
    // Даже если есть токен, но нет данных пользователя - на логин
    console.log('[Router] User data missing, redirecting to login', { to: to.path })
    next('/login')
  } else {
    next()
  }
})

// Асинхронная инициализация приложения - ГЛАВНОЕ:
// 1. Загружаем auth данные из Capacitor Preferences
// 2. Дождаемся router.isReady()
// 3. Монтируем приложение
async function initializeApp() {
  try {
    console.log('[Main] ===== App Initialization Start =====')
    console.log('[Main] Loading auth data from storage...')
    
    await authStore.loadToken()
    console.log('[Main] Token loaded:', !!authStore.token ? `${authStore.token.substring(0, 20)}...` : 'NONE')
    
    await authStore.loadUser()
    console.log('[Main] User loaded:', authStore.user?.login || 'NONE')
    
    console.log('[Main] Auth initialization complete')
    console.log('[Main] isAuthenticated:', authStore.isAuthenticated)
    console.log('[Main] ===== App Initialization Complete =====')
  } catch (err) {
    console.error('[Main] Error loading auth data:', err)
  }
}

// Инициализируем auth и монтируем приложение
initializeApp().then(() => {
  console.log('[Main] Auth ready, waiting for router...')
  router.isReady().then(() => {
    console.log('[Main] Router ready, mounting app...')
    app.mount('#app')
    console.log('[Main] App mounted successfully')
  })
})
