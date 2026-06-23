/**
 * Утилиты для кэширования данных в Capacitor Preferences для офлайн режима
 */

import StorageManager from './storageManager'

export const CACHE_KEYS = {
  WAYBILLS: 'cache_waybills',
  WAYBILL_DETAIL: 'cache_waybill_detail_',
  TIMESTAMP: 'cache_timestamp_',
}

export const CACHE_DURATION = 1000 * 60 * 60 * 24 // 1 день

/**
 * Сохраняет данные в кэш
 */
export const setCacheData = async (key, data) => {
  try {
    const cacheData = {
      data,
      timestamp: Date.now(),
    }
    await StorageManager.setItem(key, JSON.stringify(cacheData))
  } catch (err) {
    console.error('[CacheUtils] Error setting cache:', err)
  }
}

/**
 * Получает данные из кэша если они ещё актуальны
 */
export const getCacheData = async (key) => {
  try {
    const cached = await StorageManager.getItem(key)
    if (!cached) return null

    const { data, timestamp } = JSON.parse(cached)
    
    // Проверяем, не истёк ли кэш
    if (Date.now() - timestamp > CACHE_DURATION) {
      await StorageManager.removeItem(key)
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
export const clearCache = async (key) => {
  try {
    await StorageManager.removeItem(key)
  } catch (err) {
    console.error('[CacheUtils] Error clearing cache:', err)
  }
}

/**
 * Очищает все кэши
 */
export const clearAllCache = async () => {
  try {
    const keys = await StorageManager.keys()
    for (const key of keys) {
      if (key.startsWith('cache_')) {
        await StorageManager.removeItem(key)
      }
    }
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
 * Определяет, является ли ошибка ошибкой сетевого соединения
 * (сервер не отвечает, timeout, отсутствие соединения и т.д.)
 */
export const isNetworkError = (error) => {
  // Проверяем различные типы сетевых ошибок
  if (!error) return false
  
  // Ошибки axios
  if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED' || 
      error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT' ||
      error.code === 'EHOSTUNREACH' || error.code === 'ENETUNREACH') {
    return true
  }
  
  // Проверяем сообщение об ошибке
  const message = error.message ? error.message.toLowerCase() : ''
  if (message.includes('timeout') || message.includes('network') || 
      message.includes('econnrefused') || message.includes('unreachable') ||
      message.includes('offline') || message.includes('fetch') ||
      message.includes('request failed')) {
    return true
  }
  
  // Ошибка ответа (500, 503 - server errors)
  if (error.response && error.response.status >= 500) {
    return true
  }
  
  // Нет ответа от сервера
  if (error.request && !error.response) {
    return true
  }
  
  return false
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
  isNetworkError,
  onlineStatusListener,
  CACHE_KEYS,
}
