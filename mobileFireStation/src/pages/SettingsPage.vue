<template>
  <ion-page class="page-layout">
    <ion-header :translucent="true" class="no-border">
      <ion-toolbar :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)', '--border-bottom': 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '24px' }">
        <ion-title :style="{ color: palette.dark, textAlign: 'center', width: '100%' }">Настройки</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding" :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)' }">

      <div class="space-y-6 pb-4">
        <!-- Profile Section -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <h2 class="font-bold text-lg mb-4" :style="{ color: palette.dark }">Профиль</h2>
          
          <div class="space-y-3">
            <div class="flex justify-between items-center pb-3 border-b" :style="{ borderColor: palette.light }">
              <span class="text-sm" :style="{ color: palette.medium }">Имя</span>
              <span class="font-semibold" :style="{ color: palette.dark }">{{ authStore.user?.name || 'Не указано' }}</span>
            </div>
            
            <div class="flex justify-between items-center pb-3 border-b" :style="{ borderColor: palette.light }">
              <span class="text-sm" :style="{ color: palette.medium }">Фамилия</span>
              <span class="font-semibold" :style="{ color: palette.dark }">{{ authStore.user?.surname || 'Не указано' }}</span>
            </div>
            
            <div class="flex justify-between items-center pb-3 border-b" :style="{ borderColor: palette.light }">
              <span class="text-sm" :style="{ color: palette.medium }">Логин</span>
              <span class="font-semibold" :style="{ color: palette.dark }">{{ authStore.user?.login || 'Не указано' }}</span>
            </div>
            
            <div class="flex justify-between items-center" v-if="authStore.user?.phone">
              <span class="text-sm" :style="{ color: palette.medium }">Телефон</span>
              <span class="font-semibold" :style="{ color: palette.dark }">{{ authStore.user.phone }}</span>
            </div>
          </div>
        </div>

        <!-- Application Info Section -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <h2 class="font-bold text-lg mb-4" :style="{ color: palette.dark }">Приложение</h2>
          
          <div class="space-y-3">
            <div class="flex justify-between items-center pb-3 border-b" :style="{ borderColor: palette.light }">
              <span class="text-sm" :style="{ color: palette.medium }">Версия</span>
              <span class="text-sm font-semibold" :style="{ color: palette.dark }">1.0.0</span>
            </div>
            
            <div class="flex justify-between items-center" v-if="pendingSyncCount > 0">
              <span class="text-sm" :style="{ color: palette.medium }">Операций в очереди</span>
              <span class="text-sm font-semibold" :style="{ color: palette.warning }">{{ pendingSyncCount }}</span>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <h2 class="font-bold text-lg mb-4" :style="{ color: palette.error }">Опасная зона</h2>
          
          <Button
            :label="isLoading ? 'Выходим...' : 'Выход из аккаунта'"
            variant="danger"
            :disabled="isLoading"
            :is-loading="isLoading"
            loading-text="Выходим..."
            @click="logout"
            expand="block"
          />
          
          <p class="text-xs mt-3 text-center" :style="{ color: palette.medium }">
            Ваши локальные данные будут удалены
          </p>
        </div>
      </div>

    </ion-content>

    <!-- Bottom Navigation Footer -->
    <footer-navigation />
  </ion-page>
</template>

<style scoped>
.page-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.page-layout ion-content {
  flex: 1;
  overflow: auto;
}

/* Удалить border и shadow из header */
.page-layout ion-header {
  --border-bottom: none !important;
  box-shadow: none !important;
}

.page-layout ion-header.no-border::after {
  display: none !important;
}
</style>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { palette, Button } from '../components/ui/importUi'
import { useAuthStore } from '../stores/auth'
import { getPendingSyncCount, clearSyncQueue } from '../utils/syncQueue'
import { clearAllCache } from '../utils/cacheUtils'
import FooterNavigation from '../components/FooterNavigation.vue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonIcon,
} from '@ionic/vue'

const router = useRouter()
const authStore = useAuthStore()
const isLoading = ref(false)
const pendingSyncCount = ref(getPendingSyncCount())

const logout = async () => {
  isLoading.value = true
  try {
    console.log('[SettingsPage] Starting logout...')
    
    // Очищаем кэш
    clearAllCache()
    console.log('[SettingsPage] Cache cleared')
    
    // Очищаем очередь синхронизации
    clearSyncQueue()
    console.log('[SettingsPage] Sync queue cleared')
    
    // Очищаем авторизацию
    authStore.logout()
    console.log('[SettingsPage] Auth store cleared')
    
    // Перенаправляем на логин
    console.log('[SettingsPage] Redirecting to login...')
    await router.push('/login')
    console.log('[SettingsPage] Logout complete')
  } catch (err) {
    console.error('[SettingsPage] Error logging out:', err)
    alert('Ошибка при выходе: ' + err.message)
  } finally {
    isLoading.value = false
  }
}


</script>
