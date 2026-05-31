<template>
  <ion-page class="page-layout">
    <!-- Header -->
    <ion-header :translucent="true" class="no-border">
      <ion-toolbar :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)', '--border-bottom': 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '24px' }">
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 0 16px;">
          <button @click="goBack" style="background: none; border: none; cursor: pointer; font-size: 24px;">
            ← 
          </button>
          <ion-title :style="{ color: palette.dark, textAlign: 'center', flex: 1 }">Активная поездка</ion-title>
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
          <h2 class="text-lg font-bold mb-3" :style="{ color: palette.dark }">Путевой лист №{{ trip.number }}</h2>

          <div class="space-y-2 text-sm">
            <div>
              <p class="text-xs font-medium" :style="{ color: palette.medium }">Машина</p>
              <p class="font-semibold" :style="{ color: palette.dark }">
                {{ trip.car_brand && trip.car_model ? `${trip.car_brand} ${trip.car_model}` : trip.car_name }}
              </p>
              <p class="text-xs" :style="{ color: palette.medium }">{{ trip.car_number }}</p>
            </div>
            <div>
              <p class="text-xs font-medium" :style="{ color: palette.medium }">Дата</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ formatDate(trip.date) }}</p>
            </div>
          </div>
        </div>

        <!-- Pump Mode Selection (для пожарных машин) -->
        <div v-if="trip.vehicleType === 'fire_truck'" class="mb-6 p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <h3 class="font-bold mb-4" :style="{ color: palette.dark }">Режимы работы</h3>
          
          <div class="space-y-4">
            <!-- With Pump Mode -->
            <div class="p-3 rounded-lg border-2" :style="{ 
              borderColor: activePumpMode === 'with_pump' ? palette.primary : '#e5e7eb',
              backgroundColor: activePumpMode === 'with_pump' ? palette.primary + '10' : '#f9fafb'
            }">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <p class="font-semibold" :style="{ color: palette.dark }">С насосом</p>
                  <p class="text-sm" :style="{ color: palette.medium }">{{ formatTime(workSessions.with_pump) }}</p>
                </div>
                <Button
                  :label="activeTimer === 'with_pump' ? '⏹ Остановить' : '▶ Начать'"
                  :variant="activeTimer === 'with_pump' ? 'danger' : 'primary'"
                  size="small"
                  @click="togglePumpMode('with_pump')"
                />
              </div>
              <!-- Timer Display -->
              <div v-if="activeTimer === 'with_pump'" class="text-center p-2 rounded-lg bg-blue-50 border border-blue-200">
                <p class="text-2xl font-bold" :style="{ color: palette.primary }">{{ currentTimerDisplay }}</p>
                <p class="text-xs" :style="{ color: palette.medium }">В работе...</p>
              </div>
            </div>

            <!-- Without Pump Mode -->
            <div class="p-3 rounded-lg border-2" :style="{ 
              borderColor: activePumpMode === 'without_pump' ? palette.primary : '#e5e7eb',
              backgroundColor: activePumpMode === 'without_pump' ? palette.primary + '10' : '#f9fafb'
            }">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <p class="font-semibold" :style="{ color: palette.dark }">Без насоса</p>
                  <p class="text-sm" :style="{ color: palette.medium }">{{ formatTime(workSessions.without_pump) }}</p>
                </div>
                <Button
                  :label="activeTimer === 'without_pump' ? '⏹ Остановить' : '▶ Начать'"
                  :variant="activeTimer === 'without_pump' ? 'danger' : 'primary'"
                  size="small"
                  @click="togglePumpMode('without_pump')"
                />
              </div>
              <!-- Timer Display -->
              <div v-if="activeTimer === 'without_pump'" class="text-center p-2 rounded-lg bg-blue-50 border border-blue-200">
                <p class="text-2xl font-bold" :style="{ color: palette.primary }">{{ currentTimerDisplay }}</p>
                <p class="text-xs" :style="{ color: palette.medium }">В работе...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Fueling Section -->
        <div class="mb-6 p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <h3 class="font-bold mb-4" :style="{ color: palette.dark }">Заправка</h3>

          <!-- Total Fueling Display -->
          <div class="p-3 rounded-lg mb-4" :style="{ backgroundColor: '#f9fafb', borderLeft: `4px solid ${palette.primary}` }">
            <p class="text-xs font-medium" :style="{ color: palette.medium }">Всего заправлено</p>
            <p class="text-2xl font-bold mt-1" :style="{ color: palette.primary }">{{ totalFuelingAmount.toFixed(1) }} л</p>
          </div>

          <div class="space-y-4">
            <!-- Fueling Amount -->
            <div>
              <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
                Количество литров
              </label>

              <!-- Toggle between slider and input -->
              <div class="flex gap-2 mb-3">
                <button
                  @click="inputMode = 'slider'"
                  :style="{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    backgroundColor: inputMode === 'slider' ? palette.primary : palette.light,
                    color: inputMode === 'slider' ? '#fff' : palette.dark,
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '600'
                  }"
                >
                  Ползунок
                </button>
                <button
                  @click="inputMode = 'number'"
                  :style="{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    backgroundColor: inputMode === 'number' ? palette.primary : palette.light,
                    color: inputMode === 'number' ? '#fff' : palette.dark,
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '600'
                  }"
                >
                  Число
                </button>
              </div>

              <!-- Slider Input -->
              <div v-if="inputMode === 'slider'" class="space-y-3">
                <input
                  v-model.number="fuelingAmount"
                  type="range"
                  :min="0"
                  :max="maxFueling"
                  step="0.1"
                  class="w-full"
                  :style="{ accentColor: palette.primary }"
                />
                <div class="text-center">
                  <p class="text-lg font-bold" :style="{ color: palette.primary }">{{ fuelingAmount.toFixed(1) }} л</p>
                  <p class="text-xs" :style="{ color: palette.medium }">Макс: {{ maxFueling }} л</p>
                </div>
              </div>

              <!-- Number Input -->
              <div v-if="inputMode === 'number'">
                <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
                  <ion-input
                    v-model.number="fuelingAmount"
                    type="number"
                    placeholder="Введите количество литров"
                    :min="0"
                    :max="maxFueling"
                    step="0.1"
                  />
                </ion-item>
                <p class="text-xs mt-1" :style="{ color: palette.medium }">От 0 до {{ maxFueling }} л</p>
              </div>
            </div>

            <!-- Confirm Fueling Button -->
            <Button
              label="Подтвердить заправку"
              variant="primary"
              :disabled="fuelingAmount < 0 || isSubmitting"
              :is-loading="isSubmitting"
              loading-text="Отправка..."
              @click="confirmFueling"
              expand="block"
            />
          </div>
        </div>

        <!-- Info Box -->
        <div class="p-4 rounded-lg bg-blue-50 border-l-4" :style="{ borderColor: palette.primary }">
          <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
          <p class="text-xs mt-2" :style="{ color: palette.dark }">
            Для пожарных машин: выберите режим работы, нажмите "Начать" для запуска таймера, потом "Остановить" для фиксирования времени. Введите заправку и подтвердите. После завершения всех сеансов нажмите "Завершить поездку".
          </p>
        </div>
      </div>
    </ion-content>

    <!-- Start Work Session Modal -->
    <StartWorkSessionModal
      :is-open="showStartModal"
      :mode="startModalMode"
      :is-loading="isStartingSession"
      @confirm="confirmStartSession"
      @close="showStartModal = false"
    />

    <!-- Stop Work Session Modal -->
    <StopWorkSessionModal
      :is-open="showStopModal"
      :mode="modalMode"
      :duration="modalDuration"
      :is-loading="isStoppingSession"
      @confirm="confirmStopSession"
      @close="showStopModal = false"
    />

    <!-- Fueling Confirm Modal -->
    <FuelingConfirmModal
      :is-open="showFuelingModal"
      :amount="fuelingAmount"
      :is-loading="isConfirmingFueling"
      @confirm="confirmFuelingSubmit"
      @close="showFuelingModal = false"
    />

    <!-- End Trip Confirm Modal -->
    <div v-if="showEndTripModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <!-- Overlay -->
      <div 
        class="absolute inset-0 bg-black/50"
        @click="showEndTripModal = false"
      ></div>
      
      <!-- Modal Content -->
      <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6 space-y-6">
        <!-- Icon -->
        <div class="flex justify-center">
          <div class="flex items-center justify-center w-16 h-16 rounded-full" :style="{ backgroundColor: palette.primary + '20' }">
            <img src="@/assets/free-icon-car-trip.png" alt="Trip" style="width: 40px; height: 40px; object-fit: contain;" />
          </div>
        </div>

        <!-- Title -->
        <div class="text-center">
          <h2 class="text-xl font-bold" :style="{ color: palette.dark }">Завершить поездку?</h2>
        </div>

        <!-- Info -->
        <div class="p-3 rounded-lg bg-blue-50 border-l-4" :style="{ borderColor: palette.primary }">
          <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
          <p class="text-xs mt-1" :style="{ color: palette.dark }">
            После подтверждения вы перейдёте на страницу завершения поездки, где сможете внести остаток данных и отправить информацию на сервер.
          </p>
        </div>

        <!-- Actions -->
        <div class="flex gap-3">
          <Button
            label="Отмена"
            variant="secondary"
            @click="showEndTripModal = false"
            expand="block"
          />
          <Button
            label="Завершить"
            variant="primary"
            @click="confirmEndTrip"
            :is-loading="isEndingTrip"
            loading-text="Переход..."
            expand="block"
          />
        </div>
      </div>
    </div>

    <!-- End Trip Button -->
    <div class="fixed bottom-20 left-0 right-0 p-4 z-40">
      <Button
        label="Завершить поездку"
        variant="primary"
        expand="block"
        :is-loading="isEndingTrip"
        loading-text="Переход..."
        @click="endTrip"
      />
    </div>

    <!-- Footer Navigation -->
    <footer-navigation />
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTripStore } from '../stores/trip'
import { palette, Button } from '../components/ui/importUi'
import FooterNavigation from '../components/FooterNavigation.vue'
import StartWorkSessionModal from '../components/modals/StartWorkSessionModal.vue'
import StopWorkSessionModal from '../components/modals/StopWorkSessionModal.vue'
import FuelingConfirmModal from '../components/modals/FuelingConfirmModal.vue'
import { isOnline } from '../utils/cacheUtils'
import { addSyncOperation, SYNC_QUEUE } from '../utils/syncQueue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonItem,
  IonInput,
} from '@ionic/vue'

const router = useRouter()
const tripStore = useTripStore()

const trip = computed(() => tripStore.activeTrip || {})
const error = ref('')
const fuelingAmount = ref(0)
const inputMode = ref('slider')
const isSubmitting = ref(false)

// Таймер и сессии работы
const activeTimer = ref(null) // 'with_pump', 'without_pump', или null
const activePumpMode = ref(null) // режим, выбранный пользователем (без таймера)
const currentTimerMs = ref(0)
const currentTimerDisplay = ref('00:00')
const timerInterval = ref(null)
const sessionStartTime = ref(null)

// Сохраненные сессии работы (в миллисекундах)
const workSessions = ref({
  with_pump: 0,
  without_pump: 0
})

// Modal для подтверждения остановки
const showStopModal = ref(false)
const modalMode = ref(null)
const modalDuration = ref(0)
const isStoppingSession = ref(false)

// Modal для подтверждения начала работы
const showStartModal = ref(false)
const startModalMode = ref(null)
const isStartingSession = ref(false)

// Modal для подтверждения заправки
const showFuelingModal = ref(false)
const showEndTripModal = ref(false)
const isConfirmingFueling = ref(false)

// Для завершения поездки
const isEndingTrip = ref(false)

// Максимальное количество топлива в зависимости от типа машины
const maxFueling = computed(() => {
  if (!trip.value.vehicleType) return 100
  return trip.value.vehicleType === 'fire_truck' ? 200 : 100
})

const totalFuelingAmount = computed(() => {
  if (!trip.value.fueling || !trip.value.fueling.total) return 0
  return trip.value.fueling.total
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function formatTime(ms) {
  const seconds = Math.floor(ms / 1000)
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}ч ${minutes}м ${secs}с`
  }
  if (minutes > 0) {
    return `${minutes}м ${secs}с`
  }
  return `${secs}с`
}

function formatTimeDisplay(ms) {
  const seconds = Math.floor(ms / 1000)
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  const h = String(hours).padStart(2, '0')
  const m = String(minutes).padStart(2, '0')
  const s = String(secs).padStart(2, '0')

  if (hours > 0) {
    return `${h}:${m}:${s}`
  }
  return `${m}:${s}`
}

function startTimer(mode) {
  if (activeTimer.value) {
    // Останавливаем текущий таймер
    stopTimer()
  }

  activeTimer.value = mode
  activePumpMode.value = mode
  sessionStartTime.value = Date.now()
  currentTimerMs.value = 0

  // Обновляем таймер каждые 100ms для плавного отображения
  timerInterval.value = setInterval(() => {
    currentTimerMs.value = Date.now() - sessionStartTime.value
    currentTimerDisplay.value = formatTimeDisplay(currentTimerMs.value)
  }, 100)
}

function stopTimer() {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }

  if (activeTimer.value) {
    // Показываем модаль подтверждения
    modalMode.value = activeTimer.value
    modalDuration.value = currentTimerMs.value
    showStopModal.value = true
  }
}

function togglePumpMode(mode) {
  if (activeTimer.value === mode) {
    // Останавливаем таймер
    stopTimer()
  } else {
    // Показываем модаль подтверждения перед началом
    startModalMode.value = mode
    showStartModal.value = true
  }
}

async function confirmStopSession() {
  isStoppingSession.value = true
  try {
    // Добавляем время работы в сессию
    const totalTime = workSessions.value[modalMode.value] + modalDuration.value
    workSessions.value[modalMode.value] = totalTime

    console.log(`Сеанс работы "${modalMode.value}" завершен: ${formatTime(totalTime)}`)

    // Сохраняем данные о работе в store И localStorage
    tripStore.setFuelingData({
      amount: fuelingAmount.value,
      workSessions: workSessions.value,
      recordedAt: new Date().toISOString(),
    })

    // TODO: Отправить данные на сервер если нужно

    showStopModal.value = false
    activeTimer.value = null
    currentTimerMs.value = 0
    currentTimerDisplay.value = '00:00'
  } catch (err) {
    error.value = err.message || 'Ошибка при сохранении'
    console.error('Error confirming stop session:', err)
  } finally {
    isStoppingSession.value = false
  }
}

async function confirmStartSession() {
  isStartingSession.value = true
  try {
    // Запускаем таймер для выбранного режима
    startTimer(startModalMode.value)
    showStartModal.value = false
    console.log(`Начата работа: ${startModalMode.value}`)
  } catch (err) {
    error.value = err.message || 'Ошибка при запуске работы'
    console.error('Error confirming start session:', err)
  } finally {
    isStartingSession.value = false
  }
}

function endTrip() {
  // Показываем модаль подтверждения завершения поездки
  showEndTripModal.value = true
}

async function confirmEndTrip() {
  isEndingTrip.value = true
  try {
    // Если таймер еще работает, останавливаем его
    if (activeTimer.value) {
      clearInterval(timerInterval.value)
      // Сохраняем накопленное время
      const totalTime = workSessions.value[activeTimer.value] + currentTimerMs.value
      workSessions.value[activeTimer.value] = totalTime
    }

    // Сохраняем все данные перед переходом на страницу завершения
    console.log('[ActiveTrip] Saving work sessions before ending trip:', {
      fuelingAmount: fuelingAmount.value,
      workSessions: workSessions.value
    })
    
    tripStore.setFuelingData({
      amount: fuelingAmount.value,
      workSessions: workSessions.value,
      recordedAt: new Date().toISOString(),
    })

    console.log('[ActiveTrip] Ending trip and navigating to trip-end page')

    // Закрываем модаль и переходим на страницу завершения поездки
    showEndTripModal.value = false
    await new Promise(resolve => setTimeout(resolve, 300)) // Даём время закрыться модали
    router.push('/trip-end')
  } catch (err) {
    error.value = err.message || 'Ошибка при завершении поездки'
    console.error('Error ending trip:', err)
  } finally {
    isEndingTrip.value = false
  }
}

function goBack() {
  router.back()
}

function confirmFueling() {
  error.value = ''

  // Валидация
  if (fuelingAmount.value < 0) {
    error.value = 'Количество топлива не может быть отрицательным'
    return
  }

  if (fuelingAmount.value > maxFueling.value) {
    error.value = `Максимальное количество топлива: ${maxFueling.value} л`
    return
  }

  // Показываем модаль подтверждения заправки
  showFuelingModal.value = true
}

async function confirmFuelingSubmit() {
  isConfirmingFueling.value = true
  error.value = ''

  try {
    const fuelingData = {
      amount: fuelingAmount.value,
      workSessions: workSessions.value,
      recordedAt: new Date().toISOString(),
    }

    // Сохраняем данные о заправке в store и localStorage
    tripStore.setFuelingData(fuelingData)
    console.log('[ActiveTrip] Fueling data saved locally')

    console.log('Заправка подтверждена:', fuelingData)
    
    // Очищаем форму и закрываем модаль
    fuelingAmount.value = 0
    showFuelingModal.value = false
    
    // Показываем сообщение успеха
    // TODO: добавить toast уведомление
  } catch (err) {
    error.value = err.message || 'Ошибка при сохранении данных заправки'
    console.error('Error in confirmFuelingSubmit:', err)
  } finally {
    isConfirmingFueling.value = false
  }
}

async function submitFuelingData() {
  isSubmitting.value = true
  error.value = ''

  try {
    const fuelingData = {
      amount: fuelingAmount.value,
      workSessions: workSessions.value,
      recordedAt: new Date().toISOString(),
    }

    // Сохраняем данные о заправке в store и localStorage
    tripStore.setFuelingData(fuelingData)
    console.log('[ActiveTrip] Fueling data saved locally')

    console.log('Заправка подтверждена:', fuelingData)
    
    // Очищаем форму
    fuelingAmount.value = 0
    
    // Показываем сообщение успеха
    // TODO: добавить toast уведомление
  } catch (err) {
    error.value = err.message || 'Ошибка при сохранении данных заправки'
    console.error('Error in submitFuelingData:', err)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  // Проверяем, есть ли активная поездка
  if (!tripStore.hasActiveTrip) {
    router.push('/waybills')
    return
  }

  // Проверяем валидность активной поездки
  if (!trip.value.number || !trip.value.car_number) {
    error.value = 'Обнаружена поврежденная поездка с неполными данными. Очищаю...'
    console.error('[ActiveTrip] Invalid trip detected, clearing:', trip.value)
    
    // Ждем 2 секунды чтобы пользователь увидел сообщение
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Очищаем поврежденную поездку и возвращаемся к списку
    await tripStore.clearActiveTrip()
    router.push('/waybills')
    return
  }

  // Загружаем сохраненные данные работы из trip store
  if (trip.value.workSessions) {
    workSessions.value = {
      with_pump: trip.value.workSessions.with_pump || 0,
      without_pump: trip.value.workSessions.without_pump || 0
    }
    console.log('[ActiveTrip] Work sessions loaded from store:', workSessions.value)
  }
})

onUnmounted(() => {
  // Очищаем таймер при выходе со страницы
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }

  // Сохраняем состояние в store перед выходом
  if (tripStore.hasActiveTrip) {
    tripStore.setFuelingData({
      amount: fuelingAmount.value,
      workSessions: workSessions.value,
      recordedAt: new Date().toISOString(),
    })
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

input[type="range"] {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #e5e7eb 0%, #e5e7eb 100%);
  outline: none;
  -webkit-appearance: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: v-bind(palette.primary);
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: v-bind(palette.primary);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>
