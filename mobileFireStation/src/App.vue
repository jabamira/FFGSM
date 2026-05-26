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

const tripStore = useTripStore()
const authStore = useAuthStore()

// Инициализируем приложение при загрузке
onMounted(async () => {
  initStatusBar()
  
  console.log('[App] ===== App Mount Start =====')
  console.log('[App] Auth state at mount:', {
    isAuthenticated: authStore.isAuthenticated,
    hasToken: !!authStore.token,
    hasUser: !!authStore.user
  })
  
  // Загружаем сохраненную поездку из localStorage при старте приложения
  const savedTrip = tripStore.loadTripFromStorage()
  if (savedTrip) {
    console.log('[App] Trip loaded from storage:', { number: savedTrip.number, car_number: savedTrip.car_number })
    
    // Проверяем валидность loaded trip
    if (!savedTrip.number || !savedTrip.car_number) {
      console.warn('[App] Invalid trip detected during mount, clearing it')
      await tripStore.clearActiveTrip()
    } else {
      console.log('[App] Valid trip loaded, keeping it')
    }
  } else {
    console.log('[App] No trip in storage')
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
