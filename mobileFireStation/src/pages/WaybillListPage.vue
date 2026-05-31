<template>
  <ion-page class="page-layout">
    <ion-header :translucent="true" class="no-border">
      <ion-toolbar :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)', '--border-bottom': 'none' }">
        <div style="width: 100%; display: flex; flex-direction: column; align-items: center; gap: 0; padding-top: 12px;">
          <div :style="{ fontSize: '20px', fontWeight: '600', color: palette.dark, width: '100%', textAlign: 'center' }">Путевыые листы</div>
          <div v-if="filteredWaybills.length > 0" :style="{ fontSize: '12px', color: palette.medium, marginTop: '4px', textAlign: 'center' }">
            Всего: {{ filteredWaybills.length }}
          </div>
        </div>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding" :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)' }">

      <!-- Offline Status Bar -->
      <div v-if="!isOnlineMode" class="mb-4 p-3 rounded-lg bg-yellow-100 border-l-4 border-yellow-500">
        <p class="text-sm text-yellow-700 font-semibold">📡 Режим офлайн</p>
        <p class="text-xs text-yellow-600">
          {{ pendingSyncCount > 0 ? `${pendingSyncCount} операции ждут синхронизации` : 'Данные могут быть неактуальны' }}
        </p>
      </div>

      <!-- Pending Sync Alert -->
      <div v-if="!isOnlineMode && pendingSyncCount > 0" class="mb-4 p-3 rounded-lg bg-blue-100 border-l-4 border-blue-500">
        <p class="text-sm text-blue-700 font-semibold">⏳ Синхронизация данных</p>
        <p class="text-xs text-blue-600">{{ pendingSyncCount }} операции синхронизируются с сервером</p>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="mb-4 p-4 rounded-lg bg-red-100 border-l-4 border-red-500">
        <p class="text-sm text-red-700">{{ error }}</p>
      </div>

      <!-- Поиск и фильтры (всегда видны когда есть путевые листы) -->
      <div v-if="waybills.length > 0" class="mb-4 space-y-3">
        <!-- Поиск -->
        <ion-searchbar
          v-model="searchText"
          placeholder="Поиск по номеру или машине..."
          clear-icon="close-circle"
        ></ion-searchbar>

        <!-- Фильтр по типам машин -->
        <div class="flex gap-2">
          <ion-button
            @click="vehicleFilter = 'all'"
            :fill="vehicleFilter === 'all' ? 'solid' : 'outline'"
            size="small"
            expand="block"
            :color="vehicleFilter === 'all' ? 'primary' : undefined"
            class="filter-button"
            :class="{ 'active': vehicleFilter === 'all' }"
          >
            Все
          </ion-button>
          <ion-button
            @click="vehicleFilter = 'fire_truck'"
            :fill="vehicleFilter === 'fire_truck' ? 'solid' : 'outline'"
            size="small"
            expand="block"
            :color="vehicleFilter === 'fire_truck' ? 'primary' : undefined"
            class="filter-button"
            :class="{ 'active': vehicleFilter === 'fire_truck' }"
          >
            🚒 Пожарные
          </ion-button>
          <ion-button
            @click="vehicleFilter = 'passenger_car'"
            :fill="vehicleFilter === 'passenger_car' ? 'solid' : 'outline'"
            size="small"
            expand="block"
            :color="vehicleFilter === 'passenger_car' ? 'primary' : undefined"
            class="filter-button"
            :class="{ 'active': vehicleFilter === 'passenger_car' }"
          >
            🚗 Легковые
          </ion-button>
        </div>
      </div>

      <!-- Loading State (показываем спиннер вместо списка) -->
      <div v-if="isLoading" class="flex justify-center items-center" style="height: 300px;">
        <ion-spinner name="crescent" color="primary"></ion-spinner>
      </div>

      <!-- Список путевых листов в виде карточек -->
      <div v-else-if="waybills.length > 0 && filteredWaybills.length > 0" class="space-y-4 pb-4">
        <div
          v-for="waybill in filteredWaybills"
          :key="waybill.id"
          class="cursor-pointer transform transition hover:scale-105"
        >
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff', borderLeft: `4px solid ${palette.primary}` }">
            <!-- Header -->
            <div class="flex justify-between items-start mb-3">
              <div>
                <h2 class="text-lg font-bold" :style="{ color: palette.dark }">Путевой лист №{{ waybill.number }}</h2>
                <p class="text-xs" :style="{ color: palette.medium }">{{ formatDate(waybill.date) }}</p>
              </div>
            </div>

            <!-- Vehicle Info -->
            <div class="mb-3 p-3 rounded-lg" :style="{ backgroundColor: palette.light + '10' }">
              <p class="text-sm font-medium" :style="{ color: palette.dark }">{{ waybill.car_brand && waybill.car_model ? `${waybill.car_brand} ${waybill.car_model}` : (waybill.car_name || 'Машина') }}</p>
              <p class="text-xs" :style="{ color: palette.medium }">{{ waybill.car_number || 'Без номера' }}</p>
            </div>

            <!-- Action Button -->
            <Button
              :label="isStarting === waybill.id ? 'Загрузка...' : 'Начать поездку'"
              variant="primary"
              :disabled="isStarting === waybill.id"
              :is-loading="isStarting === waybill.id"
              loading-text="Загрузка..."
              @click.stop="startTrip(waybill.id)"
              expand="block"
            />
          </div>
        </div>
      </div>

      <!-- Пустой список (когда нет результатов) -->
      <div v-else-if="waybills.length > 0 && filteredWaybills.length === 0" class="flex flex-col items-center justify-center h-96 px-6">
        <ion-icon name="document-outline" style="font-size: 64px; color: #ccc; margin-bottom: 16px;"></ion-icon>
        <p class="text-gray-500 text-center w-full">На сегодня путевых листов не найдено</p>
        <p class="text-gray-400 text-sm mt-2">Когда появятся новые путевые листы, они отобразятся здесь</p>
        
        <!-- Кнопка обновить -->
        <div class="mt-6 flex justify-center">
          <Button
            :label="isLoading ? 'Загрузка...' : 'Обновить'"
            variant="primary"
            :disabled="isLoading"
            :is-loading="isLoading"
            loading-text="Загрузка..."
            @click="loadWaybills"
          />
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

.filter-button {
  --padding-start: 8px;
  --padding-end: 8px;
  font-size: 12px;
  font-weight: 600;
  --background: #e8e8e8;
  --color: #405267;
}

.filter-button.active {
  --background: #3b82f6;
  --color: #ffffff;
  --border-color: #3b82f6;
}

.refresh-button {
  --padding-start: 24px;
  --padding-end: 24px;
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { waybillApi } from '../api'
import { palette, Button } from '../components/ui/importUi'
import { getCacheData, setCacheData, isOnline, onlineStatusListener, CACHE_KEYS } from '../utils/cacheUtils'
import { getPendingSyncCount } from '../utils/syncQueue'
import { useAuthStore } from '../stores/auth'
import { useTripStore } from '../stores/trip'
import { getNovosibirskDate } from '../utils'
import FooterNavigation from '../components/FooterNavigation.vue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonMenuButton,
  IonSearchbar,
  IonIcon,
  IonSpinner,
  IonButton,
} from '@ionic/vue'

const router = useRouter()
const authStore = useAuthStore()
const tripStore = useTripStore()
const searchText = ref('')
const vehicleFilter = ref('all')
const waybills = ref([])
const isLoading = ref(false)
const isStarting = ref(null)
const error = ref('')
const isOnlineMode = ref(isOnline())
const pendingSyncCount = ref(getPendingSyncCount())

const filteredWaybills = computed(() => {
  // Фильтруем только путевые листы на сегодня (по времени Новосибирска)
  const today = getNovosibirskDate()
  console.log('[WaybillListPage] Today date (Novosibirsk):', today)
  console.log('[WaybillListPage] All waybills:', waybills.value.map(w => ({ id: w.id, date: w.date })))
  
  let filtered = waybills.value.filter(w => w.date === today)
  
  console.log('[WaybillListPage] Filtered by today:', filtered.length)
  
  // Сортируем: сначала пожарные, потом легковые
  filtered.sort((a, b) => {
    const typeOrder = { fire_truck: 0, passenger_car: 1 }
    return (typeOrder[a.vehicleType] || 2) - (typeOrder[b.vehicleType] || 2)
  })
  
  // Фильтруем по типу машины
  if (vehicleFilter.value !== 'all') {
    filtered = filtered.filter(w => w.vehicleType === vehicleFilter.value)
  }
  
  // Применяем поиск
  if (!searchText.value) return filtered
  return filtered.filter(w =>
    w.number.toLowerCase().includes(searchText.value.toLowerCase()) ||
    (w.car_name && w.car_name.toLowerCase().includes(searchText.value.toLowerCase())) ||
    (w.car_number && w.car_number.includes(searchText.value))
  )
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' })
}

const getStatusColor = (waybill) => {
  if (waybill.deleted_at) return palette.error
  if (waybill.availability_upon_delivery && parseFloat(waybill.availability_upon_delivery) > parseFloat(waybill.upon_issuance)) return palette.success
  return palette.warning
}

const loadWaybills = async () => {
  isLoading.value = true
  error.value = ''
  try {
    // Проверяем, авторизован ли пользователь
    if (!authStore.user || !authStore.user.id) {
      error.value = 'Пожалуйста, авторизуйтесь'
      return
    }
    
    // Получаем путевые листы текущего пользователя (водителя)
    const response = await waybillApi.list({ driver: authStore.user.id, include_car: 'true' })
    const data = response.data.results || response.data || []
    waybills.value = data
    
    // Отладка: выводим структуру объекта
    if (data.length > 0) {
      console.log('[WaybillListPage] Первый путевой лист:', JSON.stringify(data[0], null, 2))
    }
    
    // Сохраняем в кэш для офлайн режима
    setCacheData(CACHE_KEYS.WAYBILLS, data)
  } catch (err) {
    // Если ошибка и нет интернета, пытаемся загрузить из кэша
    if (!isOnline()) {
      const cachedData = getCacheData(CACHE_KEYS.WAYBILLS)
      if (cachedData) {
        waybills.value = cachedData
        error.value = 'Работаю в режиме офлайн. Данные могут быть неактуальны.'
      } else {
        error.value = 'Нет интернета и нет кэшированных данных'
      }
    } else {
      error.value = err.message || 'Ошибка загрузки путевых листов'
    }
    console.error('[WaybillListPage] Error loading waybills:', err)
  } finally {
    isLoading.value = false
  }
}

const selectWaybill = (id) => {
  // Переход на просмотр путевого листа
  router.push(`/waybill/${id}/view`)
}

const startTrip = async (id) => {
  // Проверяем, нет ли уже активной поездки
  if (tripStore.hasActiveTrip) {
    error.value = 'У вас уже есть активная поездка. Завершите её перед началом новой.'
    return
  }

  isStarting.value = id
  try {
    // Находим путевой лист для передачи его данных
    const waybill = waybills.value.find(w => w.id === id)
    
    if (waybill) {
      // Переход на страницу начала поездки с передачей данных
      router.push({
        path: `/waybill/${id}/start`,
        state: {
          waybillData: {
            id: waybill.id,
            number: waybill.number,
            date: waybill.date,
            car_name: waybill.car_name,
            car_number: waybill.car_number,
            car_brand: waybill.car_brand,
            car_model: waybill.car_model,
            vehicleType: waybill.vehicleType
          }
        }
      })
    }
  } catch (err) {
    error.value = err.message || 'Ошибка'
  } finally {
    isStarting.value = null
  }
}

onMounted(() => {
  loadWaybills()
  
  // Слушаем изменения статуса интернета
  const unsubscribe = onlineStatusListener((online) => {
    isOnlineMode.value = online
    if (online) {
      console.log('[WaybillListPage] Internet restored, syncing...')
      loadWaybills()
    }
  })
  
  onUnmounted(() => {
    unsubscribe()
  })
})
</script>
