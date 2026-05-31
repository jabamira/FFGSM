/**
 * Проверяет, старая ли поездка (старше 1 дня, не считая сегодня и вчера)
 * 
 * Правило: храним только поездки из сегодня и вчера, чтобы избежать проблем с полночью
 * @param {Object} trip - объект поездки
 * @returns {boolean} true если поездка старая и должна быть удалена
 */
export function isStaleTrip(trip) {
  if (!trip || !trip.date) {
    return true // Если нет даты - удаляем
  }

  try {
    // Получаем дату поездки
    const tripDate = new Date(trip.date)
    if (isNaN(tripDate.getTime())) {
      console.warn('[TripUtils] Invalid trip date:', trip.date)
      return true // Если невалидная дата - удаляем
    }

    // Получаем сегодняшнюю дату (только дата, без времени)
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    // Получаем дату вчера
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    // Нормализуем дату поездки (только дата, без времени)
    const tripDateNormalized = new Date(tripDate)
    tripDateNormalized.setHours(0, 0, 0, 0)

    // Разница в миллисекундах
    const diffMs = today.getTime() - tripDateNormalized.getTime()
    // Разница в днях
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    console.log('[TripUtils] Trip date check:', {
      tripDate: trip.date,
      today: today.toISOString().split('T')[0],
      yesterday: yesterday.toISOString().split('T')[0],
      tripDateNormalized: tripDateNormalized.toISOString().split('T')[0],
      diffDays: diffDays,
      isStale: diffDays > 1
    })

    // Поездка старая если она старше вчера (более 1 дня назад)
    return diffDays > 1
  } catch (err) {
    console.error('[TripUtils] Error checking if trip is stale:', err)
    return true // При ошибке - удаляем для безопасности
  }
}

/**
 * Автоматически очищает старые поездки при инициализации приложения
 * @param {Object} tripStore - Pinia tripStore
 */
export async function autoCleanupOldTrips(tripStore) {
  try {
    console.log('[TripUtils] Starting auto-cleanup of old trips...')
    
    const currentTrip = tripStore.getTripData()
    
    if (currentTrip && isStaleTrip(currentTrip)) {
      console.warn('[TripUtils] Current trip is stale, removing it:', {
        number: currentTrip.number,
        date: currentTrip.date,
        car_number: currentTrip.car_number
      })
      
      await tripStore.clearActiveTrip()
      console.log('[TripUtils] Old stale trip removed successfully')
      return true // Поездка была удалена
    }
    
    console.log('[TripUtils] Current trip is fresh or absent')
    return false // Поездка не была удалена
  } catch (err) {
    console.error('[TripUtils] Error during auto-cleanup:', err)
    return false
  }
}
