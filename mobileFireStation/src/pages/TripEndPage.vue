<template>
  <ion-page class="page-layout">
    <!-- Header -->
    <ion-header :translucent="true" class="no-border">
      <ion-toolbar :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)', '--border-bottom': 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '24px' }">
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 0 16px;">
          <button @click="goBack" style="background: none; border: none; cursor: pointer; font-size: 24px;">
            ← 
          </button>
          <ion-title :style="{ color: palette.dark, textAlign: 'center', flex: 1 }">Завершение поездки</ion-title>
          <div style="width: 24px;"></div>
        </div>
      </ion-toolbar>
    </ion-header>

    <!-- Content -->
    <ion-content :fullscreen="true" class="ion-padding" :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)' }">
      <div class="pb-24">

        <!-- Trip Info Card -->
        <div class="mb-6 p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff', borderLeft: `4px solid ${palette.primary}` }">
          <h2 class="text-lg font-bold mb-3" :style="{ color: palette.dark }">Путевой лист №{{ tripData.number }}</h2>

          <div class="space-y-2 text-sm">
            <div>
              <p class="text-xs font-medium" :style="{ color: palette.medium }">Машина</p>
              <p class="font-semibold" :style="{ color: palette.dark }">
                {{ tripData.car_brand && tripData.car_model ? `${tripData.car_brand} ${tripData.car_model}` : tripData.car_name }}
              </p>
              <p class="text-xs" :style="{ color: palette.medium }">{{ tripData.car_number }}</p>
            </div>
            <div>
              <p class="text-xs font-medium" :style="{ color: palette.medium }">Дата</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ formatDate(tripData.date) }}</p>
            </div>
          </div>
        </div>

        <!-- Fire Truck Specific Fields -->
        <div v-if="tripData.vehicleType === 'fire_truck'" class="space-y-6">
          <!-- Trip Purpose -->
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Цель выезда <span :style="{ color: '#ef4444' }">*</span>
            </label>
            <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
              <ion-input
                v-model="form.trip_purpose"
                type="text"
                placeholder="Введите цель выезда"
                maxlength="255"
              />
            </ion-item>
            <p class="text-xs mt-1" :style="{ color: palette.medium }">{{ form.trip_purpose?.length || 0 }}/255</p>
          </div>

          <!-- Trip Route (Fire Truck Only) -->
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Маршрут движения <span style="color: #ef4444;">*</span>
            </label>
            <p class="text-xs mb-2" :style="{ color: palette.medium }">До 255 символов</p>
            <ion-item class="rounded-lg border" :style="{ borderColor: errors.trip_route ? '#ef4444' : palette.light }">
              <ion-input
                v-model="form.trip_route"
                type="text"
                :placeholder="`Маршрут (машина ${tripData.car_number || 'N/A'})`"
                maxlength="255"
              />
            </ion-item>
            <p v-if="errors.trip_route" class="text-xs mt-1" style="color: #ef4444;">{{ errors.trip_route }}</p>
            <p class="text-xs mt-1" :style="{ color: palette.medium }">{{ form.trip_route?.length || 0 }}/255</p>
          </div>

          <!-- Work Sessions Display -->
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
            <h3 class="font-bold mb-4" :style="{ color: palette.dark }">Время работы</h3>
            
            <div class="space-y-3">
              <div class="p-3 rounded-lg" :style="{ backgroundColor: '#ffffff' }">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium" :style="{ color: palette.dark }">С насосом</span>
                  <span class="text-xs" :style="{ color: palette.medium }">{{ formatWorkSessionTime(tripData.workSessions?.with_pump) }}</span>
                </div>
                <input
                  v-model.number="form.work_pump_time_minutes"
                  type="number"
                  min="0"
                  max="1440"
                  placeholder="Минуты"
                  class="w-full px-3 py-2 rounded border"
                  :style="{ borderColor: palette.light }"
                />
                <p class="text-xs mt-1" :style="{ color: palette.medium }">Только цифры, максимум 1440 (24 часа)</p>
              </div>

              <div class="p-3 rounded-lg" :style="{ backgroundColor: '#ffffff' }">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium" :style="{ color: palette.dark }">Без насоса</span>
                  <span class="text-xs" :style="{ color: palette.medium }">{{ formatWorkSessionTime(tripData.workSessions?.without_pump) }}</span>
                </div>
                <input
                  v-model.number="form.work_no_pump_time_minutes"
                  type="number"
                  min="0"
                  max="1440"
                  placeholder="Минуты"
                  class="w-full px-3 py-2 rounded border"
                  :style="{ borderColor: palette.light }"
                />
                <p class="text-xs mt-1" :style="{ color: palette.medium }">Только цифры, максимум 1440 (24 часа)</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Passenger Car Specific Fields -->
        <div v-if="tripData.vehicleType === 'passenger_car'" class="space-y-6">
          <!-- Trip Target/Purpose -->
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Цель выезда <span :style="{ color: '#ef4444' }">*</span>
            </label>
            <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
              <ion-select 
                v-if="!showCustomTripPurpose"
                v-model="form.trip_purpose" 
                placeholder="Выберите цель выезда"
                @ion-change="onTripPurposeChange"
              >
                <ion-select-option value="Служебная поездка">Служебная поездка</ion-select-option>
                <ion-select-option value="Деловая встреча">Деловая встреча</ion-select-option>
                <ion-select-option value="Доставка груза">Доставка груза</ion-select-option>
                <ion-select-option value="Техническое обслуживание">Техническое обслуживание</ion-select-option>
                <ion-select-option value="Прочее">Другое (свой вариант)</ion-select-option>
              </ion-select>
              <ion-input
                v-else
                v-model="form.trip_purpose"
                type="text"
                placeholder="Введите цель выезда"
                maxlength="255"
              />
            </ion-item>
            <p class="text-xs mt-1" :style="{ color: palette.medium }">{{ form.trip_purpose?.length || 0 }}/255</p>
          </div>

          <!-- City Kilometers -->
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Км по городу <span :style="{ color: '#ef4444' }">*</span>
            </label>
            <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
              <ion-input
                v-model.number="form.city_kilometers"
                type="number"
                placeholder="0"
                min="0"
                max="2000"
              />
            </ion-item>
            <p class="text-xs mt-1" :style="{ color: palette.medium }">Только цифры, максимум 2000 км</p>
          </div>

          <!-- Regional Kilometers -->
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
            <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
              Км по области <span :style="{ color: '#ef4444' }">*</span>
            </label>
            <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
              <ion-input
                v-model.number="form.regional_kilometers"
                type="number"
                placeholder="0"
                min="0"
                max="2000"
              />
            </ion-item>
            <p class="text-xs mt-1" :style="{ color: palette.medium }">Только цифры, максимум 2000 км</p>
          </div>
        </div>

        <!-- Common Fields for Both Vehicle Types -->
        
        <!-- Departure Time -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
            Время убытия
          </label>
          <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
            <ion-input
              :value="form.departure_time"
              type="time"
              :disabled="true"
              placeholder="Автоматическое"
            />
          </ion-item>
          <p class="text-xs mt-1" :style="{ color: palette.medium }">Зафиксировано автоматически с начала поездки</p>
        </div>

        <!-- Arrival Time -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
            Время прибытия
          </label>
          <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
            <ion-input
              :value="form.arrival_time"
              type="time"
              :disabled="true"
              placeholder="Автоматическое"
            />
          </ion-item>
          <p class="text-xs mt-1" :style="{ color: palette.medium }">Зафиксировано автоматически при открытии этой страницы</p>
        </div>

        <!-- Fueling Amount -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
            Заправка (л)
          </label>
          <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
            <ion-input
              v-model.number="form.fueling_amount"
              type="number"
              placeholder="0.000"
              min="0"
              :max="maxFueling"
              step="0.001"
            />
          </ion-item>
          <p class="text-xs mt-1" :style="{ color: palette.medium }">Минимум 0, максимум {{ maxFueling }}, до 3 знаков после запятой</p>
        </div>

        <!-- Fuel Consumed -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
            Израсходовано топлива (л) <span :style="{ color: '#ef4444' }">*</span>
          </label>
          <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
            <ion-input
              v-model.number="form.fuel_consumed"
              type="number"
              placeholder="0.000"
              min="0"
              max="1000"
              step="0.001"
            />
          </ion-item>
          <p class="text-xs mt-1" :style="{ color: palette.medium }">Минимум 0, максимум 1000, до 3 знаков после запятой</p>
        </div>

        <!-- Odometer Reading -->
        <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff' }">
          <label class="text-sm font-medium block mb-2" :style="{ color: palette.dark }">
            Одометр после возвращения (км) <span :style="{ color: '#ef4444' }">*</span>
          </label>
          <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
            <ion-input
              v-model.number="form.odometer_final"
              type="number"
              placeholder="0"
              min="0"
              max="999999"
            />
          </ion-item>
          <p class="text-xs mt-1" :style="{ color: palette.medium }">Только цифры, максимум 999999</p>
        </div>

        <!-- Info Box -->
        <div class="p-4 rounded-lg bg-blue-50 border-l-4 mt-6" :style="{ borderColor: palette.primary }">
          <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
          <p class="text-xs mt-2" :style="{ color: palette.dark }">
            Все поля опциональны и могут содержать значение 0. Время убытия и прибытия зафиксированы автоматически.
          </p>
        </div>

        <!-- Submit Button -->
        <Button
          label="Завершить поездку"
          variant="primary"
          expand="block"
          :is-loading="isSubmitting"
          loading-text="Сохранение..."
          @click="submitTripEnd"
          :disabled="!isFormValid || isSubmitting"
          class="mt-6 mb-4"
        />
      </div>
    </ion-content>

    <!-- Error Alert at Bottom -->
    <div v-if="error" class="fixed bottom-0 left-0 right-0 p-4 bg-red-500 text-white" style="z-index: 1000;">
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <p class="font-semibold mb-1">Ошибка</p>
          <p class="text-sm">{{ error }}</p>
        </div>
        <button @click="error = ''" class="ml-2 text-xl">&times;</button>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <!-- Overlay -->
      <div class="absolute inset-0 bg-black/50"></div>
      
      <!-- Modal Content -->
      <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6 space-y-6 text-center">
        <!-- Icon -->
        <div class="flex justify-center">
          <div class="flex items-center justify-center w-20 h-20 rounded-full" :style="{ backgroundColor: palette.primary + '20' }">
            <img  :src="carIcon" alt="Success" style="width: 50px; height: 50px; object-fit: contain;" />
          </div>
        </div>

        <!-- Title -->
        <div>
          <h2 class="text-2xl font-bold" :style="{ color: palette.dark }">Поездка завершена!</h2>
        </div>

        <!-- Message -->
        <div class="p-3 rounded-lg bg-green-50 border-l-4" :style="{ borderColor: '#10b981' }">
          <p class="text-sm" :style="{ color: '#047857' }">
            ✓ Путевой лист успешно создан и сохранён на сервере
          </p>
        </div>

        <!-- Loading indicator -->
        <div class="flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2" :style="{ borderColor: palette.primary }"></div>
        </div>
      </div>
    </div>

    <!-- Footer Navigation -->
    <footer-navigation />
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTripStore } from '../stores/trip'
import { palette, Button } from '../components/ui/importUi'
import FooterNavigation from '../components/FooterNavigation.vue'
import { isOnline } from '../utils/cacheUtils'
import { addSyncOperation, SYNC_QUEUE } from '../utils/syncQueue'
import { passengerCarRecordApi, fireTruckRecordApi } from '../api'
import carIcon from '@/assets/free-icon-car-trip.png'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonItem,
  IonInput,
  IonSelect,
  IonSelectOption,
} from '@ionic/vue'

const router = useRouter()
const tripStore = useTripStore()
const error = ref('')
const errors = ref({})
const isSubmitting = ref(false)
const showCustomTripPurpose = ref(false)
const showSuccessModal = ref(false)
const submitSuccess = ref(false)

const tripData = computed(() => tripStore.activeTrip || {})

const form = ref({
  trip_purpose: '',
  trip_route: '',
  departure_time: '',
  arrival_time: '',
  fueling_amount: 0,
  fuel_consumed: 0,
  odometer_final: 0,
  work_pump_time_minutes: 0,
  work_no_pump_time_minutes: 0,
  city_kilometers: 0,
  regional_kilometers: 0,
})

const maxFueling = computed(() => {
  if (!tripData.value.vehicleType) return 100
  return tripData.value.vehicleType === 'fire_truck' ? 200 : 100
})

const isFormValid = computed(() => {
  // Для пожарной машины нужна цель выезда
  if (tripData.value.vehicleType === 'fire_truck' && !form.value.trip_purpose) {
    return false
  }
  
  // Для легковой машины нужны цель выезда, км по городу и области
  if (tripData.value.vehicleType === 'passenger_car') {
    if (!form.value.trip_purpose) {
      return false
    }
    if (form.value.city_kilometers < 0 || form.value.regional_kilometers < 0) {
      return false
    }
  }

  // Проверяем что одометр положительный (если указан)
  if (form.value.odometer_final < 0) {
    return false
  }

  // Проверяем что расход не отрицательный
  if (form.value.fuel_consumed < 0) {
    return false
  }

  return true
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

function formatWorkSessionTime(ms) {
  if (!ms || ms === 0) return '0 мин'
  const totalSeconds = Math.floor(ms / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}ч ${minutes} мин`
  }
  return `${minutes} мин`
}

async function submitTripEnd() {
  error.value = ''
  isSubmitting.value = true

  try {
    // Валидация
    if (form.value.fuel_consumed < 0) {
      throw new Error('Расход топлива не может быть отрицательным')
    }

    if (tripData.value.vehicleType === 'fire_truck') {
      if (!form.value.trip_purpose) {
        errors.value.trip_purpose = 'Укажите цель выезда'
        throw new Error('Укажите цель выезда')
      }
      if (!form.value.trip_route || form.value.trip_route.trim() === '') {
        errors.value.trip_route = 'Маршрут движения обязателен'
        throw new Error('Укажите маршрут движения')
      }
    }

    if (tripData.value.vehicleType === 'passenger_car') {
      if (!form.value.trip_purpose) {
        errors.value.trip_purpose = 'Укажите цель выезда'
        throw new Error('Укажите цель выезда')
      }
      if (form.value.city_kilometers < 0 || form.value.regional_kilometers < 0) {
        throw new Error('Количество км не может быть отрицательным')
      }
    }

    // Очищаем ошибки валидации
    errors.value = {}

    // Строим данные для отправки в зависимости от типа машины
    let recordData = {}
    let submitSuccess = false

    if (tripData.value.vehicleType === 'passenger_car') {
      // Данные для PassengerCarWaybillRecord
      recordData = {
        passenger_car_waybill: tripData.value.waybillId,
        target: form.value.trip_purpose,
        departure_time: form.value.departure_time,
        arrival_time: form.value.arrival_time,
        distance_city_km: form.value.city_kilometers,
        distance_area_km: form.value.regional_kilometers,
        fuel_refueled: form.value.fueling_amount,
        fuel_used: form.value.fuel_consumed,
      }

      console.log('[TripEnd] Passenger car record data before send:', {
        recordData,
        formData: {
          fueling_amount: form.value.fueling_amount,
          fuel_consumed: form.value.fuel_consumed,
          city_kilometers: form.value.city_kilometers,
          regional_kilometers: form.value.regional_kilometers,
          trip_purpose: form.value.trip_purpose
        }
      })

      // Отправляем на сервер
      if (isOnline()) {
        try {
          console.log('[TripEnd] Sending passenger car record:', recordData)
          const response = await passengerCarRecordApi.create(recordData)
          console.log('[TripEnd] Passenger car record created successfully:', response)
          submitSuccess = true
        } catch (err) {
          console.error('[TripEnd] Error creating passenger car record:', err)
          console.error('[TripEnd] Error response:', err.response?.data)
          console.error('[TripEnd] Error message:', err.message)
          
          // Выводим понятное сообщение об ошибке
          let errorMsg = 'Ошибка при сохранении данных поездки'
          if (err.response?.data) {
            if (Array.isArray(err.response.data)) {
              errorMsg = err.response.data.join(', ')
            } else if (err.response.data.detail) {
              errorMsg = err.response.data.detail
            } else if (err.response.data.non_field_errors) {
              errorMsg = err.response.data.non_field_errors.join(', ')
            } else if (typeof err.response.data === 'string') {
              errorMsg = err.response.data
            }
          }
          error.value = errorMsg
          console.log('[TripEnd] Final error message:', errorMsg)
          submitSuccess = false
        }
      } else {
        // Офлайн режим - сохраняем в синхронизацию
        addSyncOperation(SYNC_QUEUE.TRIP_END, recordData)
        console.log('[TripEnd] Record creation saved for sync')
      }
    } else if (tripData.value.vehicleType === 'fire_truck') {
      // Данные для FireTruckWaybillRecord
      recordData = {
        fire_truck_waybill: tripData.value.waybillId,
        target: form.value.trip_purpose,
        departure_time: form.value.departure_time,
        arrival_time: form.value.arrival_time,
        odometer_after: form.value.odometer_final,
        time_with_pump: form.value.work_pump_time_minutes,
        time_without_pump: form.value.work_no_pump_time_minutes,
        fuel_refueled: form.value.fueling_amount,
        fuel_used: form.value.fuel_consumed,
      }

      // Добавляем маршрут если есть
      if (form.value.trip_route) {
        recordData.driving_route = form.value.trip_route
      }

      console.log('[TripEnd] Fire truck record data before send:', {
        recordData,
        formData: {
          work_pump_time_minutes: form.value.work_pump_time_minutes,
          work_no_pump_time_minutes: form.value.work_no_pump_time_minutes,
          fueling_amount: form.value.fueling_amount,
          fuel_consumed: form.value.fuel_consumed,
          odometer_final: form.value.odometer_final,
          trip_purpose: form.value.trip_purpose,
          trip_route: form.value.trip_route
        }
      })

      // Отправляем на сервер
      if (isOnline()) {
        try {
          console.log('[TripEnd] Sending fire truck record:', recordData)
          const response = await fireTruckRecordApi.create(recordData)
          console.log('[TripEnd] Fire truck record created successfully:', response)
          submitSuccess = true
        } catch (err) {
          console.error('[TripEnd] Error creating fire truck record:', err)
          console.error('[TripEnd] Error response:', err.response?.data)
          console.error('[TripEnd] Error message:', err.message)
          
          // Выводим понятное сообщение об ошибке
          let errorMsg = 'Ошибка при сохранении данных поездки'
          if (err.response?.data) {
            if (Array.isArray(err.response.data)) {
              // Если это массив ошибок (например, 'Не найдены последние показания')
              const errorMessages = err.response.data
              if (errorMessages[0] && errorMessages[0].includes('Не найдены последние показания')) {
                errorMsg = 'Для этой машины нет начальных данных (одометр и топливо). Создайте запись в журнале одометра перед началом поездки.'
              } else {
                errorMsg = errorMessages.join(', ')
              }
            } else if (err.response.data.detail) {
              errorMsg = err.response.data.detail
            } else if (err.response.data.non_field_errors) {
              errorMsg = err.response.data.non_field_errors.join(', ')
            } else if (typeof err.response.data === 'string') {
              errorMsg = err.response.data
            }
          }
          error.value = errorMsg
          console.log('[TripEnd] Final error message:', errorMsg)
          submitSuccess = false
        }
      } else {
        // Офлайн режим - сохраняем в синхронизацию
        addSyncOperation(SYNC_QUEUE.TRIP_END, recordData)
        console.log('[TripEnd] Record creation saved for sync')
      }
    }

    // Очищаем store и переходим на список путевых листов только если успешно отправлено
    console.log('[TripEnd] Submit success:', submitSuccess, 'Online:', isOnline())
    if (submitSuccess || !isOnline()) {
      console.log('[TripEnd] Showing success modal and clearing active trip')
      showSuccessModal.value = true
      // Закрываем модаль через 3 секунды и переходим
      setTimeout(async () => {
        await tripStore.clearActiveTrip()
        router.push('/waybills')
      }, 2000)
    } else {
      console.warn('[TripEnd] Submit failed and we are online - not clearing data')
    }
  } catch (err) {
    error.value = err.message || 'Ошибка при завершении поездки'
    console.error('Error in submitTripEnd:', err)
  } finally {
    isSubmitting.value = false
  }
}

function onTripPurposeChange(event) {
  if (event.detail.value === 'Прочее') {
    showCustomTripPurpose.value = true
    form.value.trip_purpose = ''
  } else {
    showCustomTripPurpose.value = false
    form.value.trip_purpose = event.detail.value
  }
}

function goBack() {
  router.back()
}

onMounted(() => {
  // Проверяем, есть ли активная поездка
  console.log('[TripEnd] onMounted: Checking active trip')
  console.log('[TripEnd] activeTrip:', tripStore.activeTrip)
  console.log('[TripEnd] tripData:', tripData.value)
  
  if (!tripStore.hasActiveTrip) {
    console.log('[TripEnd] No active trip found, redirecting to waybills')
    router.push('/waybills')
  }

  // Загружаем цель выезда и маршрут из tripData если они там есть
  if (tripData.value.tripPurpose) {
    form.value.trip_purpose = tripData.value.tripPurpose
    console.log('[TripEnd] Loaded trip_purpose from tripData:', form.value.trip_purpose)
  }
  if (tripData.value.tripRoute) {
    form.value.trip_route = tripData.value.tripRoute
    console.log('[TripEnd] Loaded trip_route from tripData:', form.value.trip_route)
  }

  // Инициализируем время выезда из startedAt
  if (tripData.value.startedAt) {
    const startDate = new Date(tripData.value.startedAt)
    form.value.departure_time = `${String(startDate.getHours()).padStart(2, '0')}:${String(startDate.getMinutes()).padStart(2, '0')}`
  }

  // Инициализируем время прибытия текущим временем
  const now = new Date()
  form.value.arrival_time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

  // Инициализируем заправку из предыдущей страницы
  if (tripData.value.fueling && tripData.value.fueling.total) {
    form.value.fueling_amount = tripData.value.fueling.total
    console.log('[TripEnd] Fueling initialized:', form.value.fueling_amount)
  }

  // Инициализируем форму с данными работы, если они есть
  console.log('[TripEnd] Initializing workSessions:', {
    workSessions: tripData.value.workSessions,
    with_pump_ms: tripData.value.workSessions?.with_pump,
    without_pump_ms: tripData.value.workSessions?.without_pump
  })
  if (tripData.value.workSessions) {
    const pumpMinutes = Math.floor((tripData.value.workSessions.with_pump || 0) / 60000)
    const noPumpMinutes = Math.floor((tripData.value.workSessions.without_pump || 0) / 60000)
    form.value.work_pump_time_minutes = pumpMinutes
    form.value.work_no_pump_time_minutes = noPumpMinutes
    console.log('[TripEnd] Initialized work times:', {
      work_pump_time_minutes: pumpMinutes,
      work_no_pump_time_minutes: noPumpMinutes
    })
  } else {
    console.log('[TripEnd] No workSessions data available')
  }
})
</script>

<style scoped>
/* Скрыть AM/PM из input[type="time"] */
input[type="time"]::-webkit-calendar-picker-indicator {
  display: none;
}

input[type="time"]::-webkit-datetime-edit-ampm-field {
  display: none;
}

input[type="time"] {
  /* Убрать AM/PM */
}

/* Для ion-input с type="time" */
::v-deep ion-input input[type="time"]::-webkit-datetime-edit-ampm-field {
  display: none !important;
}

::v-deep ion-input input[type="time"] {
  width: 100%;
}

.page-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.page-layout ion-content {
  flex: 1;
  overflow: auto;
}

input {
  font-family: inherit;
}
</style>
