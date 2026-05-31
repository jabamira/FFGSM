<template>
  <ion-app>
    <ion-router-outlet />
    <!-- <ConsoleDisplay /> -->
  </ion-app>
</template>

<script setup>
import { IonApp, IonRouterOutlet } from '@ionic/vue'
import { onMounted } from 'vue'
import { useTripStore } from './stores/trip'
import { useAuthStore } from './stores/auth'
import ConsoleDisplay from './components/ConsoleDisplay.vue'
import { initStatusBar } from './utils/statusBar'
import { autoCleanupOldTrips } from './utils/tripUtils'

const tripStore = useTripStore()
const authStore = useAuthStore()

// Инициализируем приложение при загрузке
onMounted(async () => {
  initStatusBar()
  
  console.log('[App] ===== App Mount Start =====')
  
  // Сначала загружаем авторизацию из хранилища
  await authStore.loadToken()
  await authStore.loadUser()
  
  console.log('[App] Auth state at mount:', {
    isAuthenticated: authStore.isAuthenticated,
    hasToken: !!authStore.token,
    hasUser: !!authStore.user
  })
  
  // Проверяем если ли уже загруженная поездка (это может быть если роутер уже загрузил её)
  if (tripStore.hasActiveTrip) {
    console.log('[App] Trip already loaded by router, skipping duplicate load')
    // Проверяем валидность уже загруженной поездки
    const currentTrip = tripStore.getTripData()
    if (!currentTrip.number || !currentTrip.car_number) {
      console.warn('[App] Already loaded trip is invalid, clearing it')
      await tripStore.clearActiveTrip()
    }
  } else {
    // Загружаем поездку только если её ещё нет
    console.log('[App] No trip loaded yet, loading from storage...')
    const savedTrip = await tripStore.loadTripFromStorage()
    if (savedTrip) {
      console.log('[App] Trip loaded from storage:', { number: savedTrip.number, car_number: savedTrip.car_number })
      
      // Проверяем валидность loaded trip
      if (!savedTrip.number || !savedTrip.car_number) {
        console.warn('[App] Loaded trip is invalid, clearing it')
        await tripStore.clearActiveTrip()
      } else {
        // Проверяем, не старая ли поездка, и автоматически удаляем старые
        const wasStaleTrip = await autoCleanupOldTrips(tripStore)
        if (wasStaleTrip) {
          console.log('[App] Stale trip was auto-cleaned')
        } else {
          console.log('[App] Valid and fresh trip loaded, keeping it')
        }
      }
    } else {
      console.log('[App] No trip in storage')
    }
  }
  
  console.log('[App] ===== App Mount Complete =====')
})
</script>

<style>
#app,
html,
body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
}

ion-app {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
}

ion-router-outlet {
  flex: 1;
  overflow: hidden;
}
</style>
