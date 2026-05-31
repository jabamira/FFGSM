import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import StorageManager from '../utils/storageManager'

const STORAGE_KEY = 'active_trip_data'

export const useTripStore = defineStore('trip', () => {
  // Активная поездка
  const activeTrip = ref(null)
  const isLoading = ref(false)
  const error = ref('')

  // Проверка, есть ли активная поездка
  const hasActiveTrip = computed(() => !!activeTrip.value)

  // Сохранить поездку в Capacitor Preferences
  async function saveTripToStorage(trip) {
    try {
      await StorageManager.setItem(STORAGE_KEY, JSON.stringify(trip))
      console.log('[TripStore] Trip saved to storage')
    } catch (err) {
      console.error('[TripStore] Error saving trip to storage:', err)
    }
  }

  // Загрузить поездку из Capacitor Preferences
  async function loadTripFromStorage() {
    try {
      const tripData = await StorageManager.getItem(STORAGE_KEY)
      if (tripData) {
        const trip = JSON.parse(tripData)
        activeTrip.value = trip
        console.log('[TripStore] Trip loaded from storage')
        return trip
      }
      return null
    } catch (err) {
      console.error('[TripStore] Error loading trip from storage:', err)
      return null
    }
  }

  // Удалить поездку из Capacitor Preferences
  async function removeTripFromStorage() {
    try {
      await StorageManager.removeItem(STORAGE_KEY)
      console.log('[TripStore] Trip removed from storage')
    } catch (err) {
      console.error('[TripStore] Error removing trip from storage:', err)
    }
  }

  // Начать новую поездку
  function startTrip(tripData) {
    // Валидируем что данные полные перед сохранением
    if (!tripData.number || !tripData.car_number || !tripData.waybillId || !tripData.date) {
      console.error('[TripStore] Invalid trip data, cannot start trip:', tripData)
      error.value = 'Ошибка: неполные данные путевого листа, поездка не может быть начата'
      return false
    }
    
    activeTrip.value = {
      waybillId: tripData.waybillId,
      number: tripData.number,
      date: tripData.date,
      car_name: tripData.car_name,
      car_number: tripData.car_number,
      car_brand: tripData.car_brand,
      car_model: tripData.car_model,
      vehicleType: tripData.vehicleType,
      tripPurpose: tripData.tripPurpose,
      tripRoute: tripData.tripRoute,
      departureTime: tripData.departureTime,
      startedAt: new Date().toISOString(),
      fueling: null, // Данные о заправке
      pumpMode: null, // Режим насоса (для пожарных машин)
      workSessions: { // Накопленное время работы (в миллисекундах)
        with_pump: 0,
        without_pump: 0
      }
    }
    error.value = ''
    // Сохраняем в localStorage
    saveTripToStorage(activeTrip.value)
    return true
  }

  // Завершить поездку
  async function endTrip() {
    activeTrip.value = null
    error.value = ''
    await removeTripFromStorage()
  }

  // Очистить активную поездку (невалидная или зависшая)
  async function clearActiveTrip() {
    console.warn('[TripStore] Clearing invalid/stuck active trip')
    activeTrip.value = null
    error.value = ''
    await removeTripFromStorage()
  }

  // Обновить данные о заправке
  function setFuelingData(fuelingData) {
    if (activeTrip.value) {
      // Инициализируем или восстанавливаем структуру fueling
      if (!activeTrip.value.fueling || !Array.isArray(activeTrip.value.fueling.fuelings)) {
        activeTrip.value.fueling = {
          total: 0,
          fuelings: []
        }
      }

      // Добавляем новую заправку в историю
      activeTrip.value.fueling.fuelings.push({
        amount: fuelingData.amount,
        recordedAt: fuelingData.recordedAt
      })
      
      // Пересчитываем итоговое количество
      activeTrip.value.fueling.total = activeTrip.value.fueling.fuelings.reduce(
        (sum, f) => sum + (f.amount || 0),
        0
      )

      // Обновляем workSessions, если они переданы
      if (fuelingData.workSessions) {
        console.log('[TripStore] Updating workSessions:', {
          previous: activeTrip.value.workSessions,
          new: fuelingData.workSessions
        })
        activeTrip.value.workSessions = fuelingData.workSessions
        console.log('[TripStore] WorkSessions updated:', activeTrip.value.workSessions)
      }
      // Сохраняем обновленные данные в localStorage
      saveTripToStorage(activeTrip.value)
      console.log('[TripStore] Fueling data updated. Total:', activeTrip.value.fueling.total, 'Entries:', activeTrip.value.fueling.fuelings.length, 'WorkSessions:', activeTrip.value.workSessions)
    }
  }

  // Обновить режим насоса
  function setPumpMode(mode) {
    if (activeTrip.value) {
      activeTrip.value.pumpMode = mode // 'with_pump', 'without_pump', или null для легковых
    }
  }

  // Установить ошибку
  function setError(errorMsg) {
    error.value = errorMsg
  }

  // Очистить ошибку
  function clearError() {
    error.value = ''
  }

  // Установить статус загрузки
  function setLoading(isLoadingState) {
    isLoading.value = isLoadingState
  }

  // Получить данные активной поездки
  function getTripData() {
    return activeTrip.value
  }

  return {
    activeTrip,
    isLoading,
    error,
    hasActiveTrip,
    startTrip,
    endTrip,
    clearActiveTrip,
    setFuelingData,
    setPumpMode,
    setError,
    clearError,
    setLoading,
    getTripData,
    saveTripToStorage,
    loadTripFromStorage,
    removeTripFromStorage,
  }
})
