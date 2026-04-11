/**
 * Утилиты для кэширования данных в localStorage для офлайн режима
 */

export const CACHE_KEYS = {
  WAYBILLS: 'cache_waybills',
  WAYBILL_DETAIL: 'cache_waybill_detail_',
  TIMESTAMP: 'cache_timestamp_',
}

export const CACHE_DURATION = 1000 * 60 * 60 * 24 // 1 день

/**
 * Сохраняет данные в кэш
 */
export const setCacheData = (key, data) => {
  try {
    const cacheData = {
      data,
      timestamp: Date.now(),
    }
    localStorage.setItem(key, JSON.stringify(cacheData))
  } catch (err) {
    console.error('[CacheUtils] Error setting cache:', err)
  }
}

/**
 * Получает данные из кэша если они ещё актуальны
 */
export const getCacheData = (key) => {
  try {
    const cached = localStorage.getItem(key)
    if (!cached) return null

    const { data, timestamp } = JSON.parse(cached)
    
    // Проверяем, не истёк ли кэш
    if (Date.now() - timestamp > CACHE_DURATION) {
      localStorage.removeItem(key)
      return null
    }

    return data
  } catch (err) {
    console.error('[CacheUtils] Error getting cache:', err)
    return null
  }
}

/**
 * Очищает кэш
 */
export const clearCache = (key) => {
  try {
    localStorage.removeItem(key)
  } catch (err) {
    console.error('[CacheUtils] Error clearing cache:', err)
  }
}

/**
 * Очищает все кэши
 */
export const clearAllCache = () => {
  try {
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('cache_')) {
        localStorage.removeItem(key)
      }
    })
  } catch (err) {
    console.error('[CacheUtils] Error clearing all cache:', err)
  }
}

/**
 * Проверяет, есть ли интернет
 */
export const isOnline = () => {
  return navigator.onLine
}

/**
 * Слушает изменения статуса интернета
 */
export const onlineStatusListener = (callback) => {
  window.addEventListener('online', () => callback(true))
  window.addEventListener('offline', () => callback(false))
}

export default {
  setCacheData,
  getCacheData,
  clearCache,
  clearAllCache,
  isOnline,
  onlineStatusListener,
  CACHE_KEYS,
}
