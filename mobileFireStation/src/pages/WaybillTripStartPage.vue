<template>
  <ion-page class="page-layout">
    <!-- Header -->
    <ion-header :translucent="true" class="no-border">
      <ion-toolbar :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)', '--border-bottom': 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '24px' }">
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 0 16px;">
          <button @click="goBack" style="background: none; border: none; cursor: pointer; font-size: 24px;">
            ← 
          </button>
          <ion-title :style="{ color: palette.dark, textAlign: 'center', flex: 1 }">Начало поездки</ion-title>
          <div style="width: 24px;"></div>
        </div>
      </ion-toolbar>
    </ion-header>

    <!-- Content -->
    <ion-content :fullscreen="true" class="ion-padding" :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)' }">
      <div class="pb-4">
        <!-- Error Alert -->
        <div v-if="error" class="mb-4 p-4 rounded-lg bg-red-100 border-l-4 border-red-500">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <!-- Trip Info Card -->
        <div class="mb-6 p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff', borderLeft: `4px solid ${palette.primary}` }">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold" :style="{ color: palette.dark }">{{ waybill.number ? `Путевой лист №${waybill.number}` : 'Путевой лист' }}</h2>
          </div>

          <!-- Vehicle Info -->
          <div class="space-y-2 text-sm">
            <div>
              <p class="text-xs font-medium" :style="{ color: palette.medium }">Машина</p>
              <p class="font-semibold" :style="{ color: palette.dark }">
                {{ waybill.car_brand && waybill.car_model ? `${waybill.car_brand} ${waybill.car_model}` : (waybill.car_name || 'Машина') }}
              </p>
              <p class="text-xs" :style="{ color: palette.medium }">{{ waybill.car_number || 'Без номера' }}</p>
            </div>
            <div>
              <p class="text-xs font-medium" :style="{ color: palette.medium }">Дата</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ formatDate(waybill.date) }}</p>
            </div>
          </div>
        </div>

        <!-- Form -->
        <div class="space-y-4">
          <!-- Trip Purpose -->
          <div>
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Цель выезда
              <span :style="{ color: palette.medium }">(опционально)</span>
            </label>
            <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
              <ion-input
                v-model="form.tripPurpose"
                type="text"
                placeholder="Введите цель выезда"
                maxlength="255"
                @ion-blur="validateTripPurpose"
              />
            </ion-item>
            <div class="flex justify-between items-center mt-1">
              <p v-if="errors.tripPurpose" class="text-xs text-red-500">{{ errors.tripPurpose }}</p>
              <p class="text-xs ml-auto" :style="{ color: palette.medium }">{{ form.tripPurpose.length }}/255</p>
            </div>
          </div>

          <!-- Trip Route -->
          <div>
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Маршрут движения
              <span :style="{ color: palette.medium }">(опционально)</span>
            </label>
            <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
              <ion-input
                v-model="form.tripRoute"
                type="text"
                placeholder="Введите маршрут движения"
                maxlength="255"
                @ion-blur="validateTripRoute"
              />
            </ion-item>
            <div class="flex justify-between items-center mt-1">
              <p v-if="errors.tripRoute" class="text-xs text-red-500">{{ errors.tripRoute }}</p>
              <p class="text-xs ml-auto" :style="{ color: palette.medium }">{{ form.tripRoute.length }}/255</p>
            </div>
          </div>

          <!-- Departure Time (read-only) -->
          <div>
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Время выезда
            </label>
            <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
              <ion-input
                :value="form.departureTime"
                type="text"
                :disabled="true"
                placeholder="Автоматическое время"
              />
            </ion-item>
            <p class="text-xs mt-1" :style="{ color: palette.medium }">Время будет зафиксировано автоматически</p>
          </div>
         <div class="p-4 rounded-lg bg-blue-50 border-l-4" :style="{ borderColor: palette.primary }">
            <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
            <p class="text-xs mt-2" :style="{ color: palette.dark }">
              После нажатия "Начать поездку" потребуется подтверждение. Убедитесь, что все данные верны.
            </p>
          </div>
          <!-- Start Trip Button (before info box) -->
          <Button
            label="Начать поездку"
            variant="primary"
            :disabled="isLoading"
            :is-loading="isLoading"
            loading-text="Загрузка..."
            @click="handleStartTrip"
            expand="block"
          />
        
       

          <!-- Info Box -->
         
        </div>
      </div>
    </ion-content>

    <!-- Start Trip Confirm Modal -->
    <StartTripConfirmModal
      :is-open="showConfirmModal"
      :vehicle-info="{
        name: waybill.car_name || 'Машина',
        number: waybill.car_number || 'Без номера',
        brand: waybill.car_brand,
        model: waybill.car_model,
        vehicleType: waybill.vehicleType
      }"
      :trip-data="{
        date: waybill.date,
        time: form.departureTime,
        tripPurpose: form.tripPurpose,
        tripRoute: form.tripRoute
      }"
      :is-loading="isConfirming"
      @confirm="confirmStartTrip"
      @close="showConfirmModal = false"
    />

    <!-- Footer Navigation -->
    <footer-navigation />
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { waybillApi } from '../api'
import { palette } from '../components/ui/theme'
import { Button } from '../components/ui/importUi'
import { useAuthStore } from '../stores/auth'
import { useTripStore } from '../stores/trip'
import StartTripConfirmModal from '../components/modals/StartTripConfirmModal.vue'
import FooterNavigation from '../components/FooterNavigation.vue'
import { addSyncOperation, SYNC_QUEUE, getPendingSyncCount } from '../utils/syncQueue'
import { isOnline } from '../utils/cacheUtils'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonItem,
  IonInput,
  IonSpinner,
} from '@ionic/vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const tripStore = useTripStore()

const waybillId = route.params.id
const waybill = ref({})
const isLoading = ref(false)
const isConfirming = ref(false)
const error = ref('')
const showConfirmModal = ref(false)

const form = ref({
  tripPurpose: '',
  tripRoute: '',
  departureTime: getCurrentTime()
})

const errors = ref({
  tripPurpose: '',
  tripRoute: '',
  waybill: ''
})

function isWaybillValid(wb) {
  // Проверяем что путевой лист имеет все необходимые данные
  return !!(
    wb &&
    wb.id &&
    wb.number &&
    wb.car_number &&
    (wb.car_name || (wb.car_brand && wb.car_model)) &&
    wb.date
  )
}

function getCurrentTime() {
  const now = new Date()
  return now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function validateTripPurpose() {
  errors.value.tripPurpose = ''
  if (form.value.tripPurpose.length > 255) {
    errors.value.tripPurpose = 'Максимум 255 символов'
    form.value.tripPurpose = form.value.tripPurpose.substring(0, 255)
  }
}

function validateTripRoute() {
  errors.value.tripRoute = ''
  if (form.value.tripRoute.length > 255) {
    errors.value.tripRoute = 'Максимум 255 символов'
    form.value.tripRoute = form.value.tripRoute.substring(0, 255)
  }
}

function goBack() {
  router.back()
}

function handleStartTrip() {
  validateTripPurpose()
  validateTripRoute()
  
  // Валидируем путевой лист
  errors.value.waybill = ''
  if (!isWaybillValid(waybill.value)) {
    errors.value.waybill = 'Ошибка: неполные данные путевого листа. Попробуйте перезагрузить или выберите другой путевой лист.'
    return
  }
  
  if (!errors.value.tripPurpose && !errors.value.tripRoute && !errors.value.waybill) {
    showConfirmModal.value = true
  }
}

async function confirmStartTrip() {
  isConfirming.value = true
  error.value = ''

  try {
    // Проверяем, нет ли уже активной поездки
    if (tripStore.hasActiveTrip) {
      // Проверяем валидность старой поездки
      if (!tripStore.activeTrip?.number || !tripStore.activeTrip?.car_number) {
        // Очищаем невалидную поездку
        console.warn('[WaybillTripStart] Clearing invalid active trip:', tripStore.activeTrip)
        await tripStore.clearActiveTrip()
      } else {
        error.value = 'У вас уже есть активная поездка. Завершите её перед началом новой.'
        isConfirming.value = false
        return
      }
    }
    
    // Финальная проверка перед началом поездки
    if (!isWaybillValid(waybill.value)) {
      error.value = 'Ошибка: неполные данные путевого листа. Пожалуйста, попробуйте ещё раз.'
      isConfirming.value = false
      return
    }

    // Подготавливаем данные о начале поездки
    const tripStartData = {
      waybillId: parseInt(waybillId),
      number: waybill.value.number,
      date: waybill.value.date,
      car_name: waybill.value.car_name,
      car_number: waybill.value.car_number,
      car_brand: waybill.value.car_brand,
      car_model: waybill.value.car_model,
      vehicleType: waybill.value.vehicleType,
      tripPurpose: form.value.tripPurpose,
      tripRoute: form.value.tripRoute,
      departureTime: form.value.departureTime,
      departureDate: waybill.value.date,
      startedAt: new Date().toISOString(),
    }

    console.log('Начало поездки:', tripStartData)

    // Сохраняем активную поездку в store
    const startResult = tripStore.startTrip(tripStartData)
    
    if (!startResult) {
      error.value = tripStore.error || 'Ошибка при сохранении данных поездки'
      isConfirming.value = false
      return
    }

    // Добавляем операцию в очередь синхронизации для офлайн режима
    const syncAdded = addSyncOperation(SYNC_QUEUE.TRIP_START, tripStartData)
    console.log('[WaybillTripStart] Sync operation added:', syncAdded)
    console.log('[WaybillTripStart] Trip data saved locally - will be sent when creating waybill record')

    // Имитируем задержку сохранения
    await new Promise(resolve => setTimeout(resolve, 800))

    // Закрываем модаль
    showConfirmModal.value = false

    // Переходим на страницу активной поездки
    router.push('/trip/active')
  } catch (err) {
    error.value = err.message || 'Ошибка при начале поездки'
    console.error('Error starting trip:', err)
  } finally {
    isConfirming.value = false
  }
}

async function loadWaybill() {
  isLoading.value = true
  error.value = ''

  try {
    // Сначала проверяем, есть ли данные переданные со страницы списка
    const waybillFromState = router.currentRoute.value.state?.waybillData
    
    if (waybillFromState) {
      // Используем переданные данные
      waybill.value = waybillFromState
      console.log('Waybill loaded from state:', waybill.value)
      
      // Опционально: проверяем данные на сервере для верификации
      try {
        await verifyWaybillData(waybillFromState.id, waybillFromState.number)
      } catch (verifyErr) {
        console.warn('[WaybillTripStart] Verification warning:', verifyErr)
        // Продолжаем даже если верификация не удалась
      }
    } else {
      // Fallback: загружаем с сервера, если данные не переданы
      if (!authStore.user || !authStore.user.id) {
        error.value = 'Пожалуйста, авторизуйтесь'
        return
      }

      const response = await waybillApi.list({ driver: authStore.user.id, include_car: 'true' })
      const data = response.data || []
      const foundWaybill = data.find(w => w.id === parseInt(waybillId))
      
      if (foundWaybill) {
        if (isWaybillValid(foundWaybill)) {
          waybill.value = foundWaybill
          console.log('Waybill loaded from server:', waybill.value)
        } else {
          error.value = 'Путевой лист содержит неполные данные. Пожалуйста, проверьте данные машины и попробуйте ещё раз.'
          console.error('Invalid waybill data:', foundWaybill)
        }
      } else {
        error.value = 'Путевой лист не найден'
      }
    }
  } catch (err) {
    error.value = err.message || 'Ошибка загрузки путевого листа'
    console.error('Error loading waybill:', err)
  } finally {
    isLoading.value = false
  }
}

async function verifyWaybillData(waybillId, waybillNumber) {
  // Проверяем данные путевого листа на сервере для верификации
  try {
    const response = await waybillApi.get(waybillId)
    if (response.data) {
      console.log('[WaybillTripStart] Data verified on server')
      return true
    }
  } catch (err) {
    console.error('[WaybillTripStart] Verification failed:', err)
    throw err
  }
}

onMounted(() => {
  // Обновляем время выезда при каждой загрузке страницы
  form.value.departureTime = getCurrentTime()
  
  if (waybillId) {
    loadWaybill()
  }
})
</script>

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

ion-spinner {
  display: inline-block;
}
</style>
