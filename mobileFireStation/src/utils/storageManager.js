/**
 * Менеджер хранилища - обертка для Capacitor Preferences API
 * Работает как на web, так и на native (iOS/Android)
 */

import { Preferences } from '@capacitor/preferences'

class StorageManager {
  /**
   * Получить значение из хранилища
   * @param {string} key - Ключ
   * @returns {Promise<string|null>} - Значение или null
   */
  static async getItem(key) {
    try {
      const { value } = await Preferences.get({ key })
      return value || null
    } catch (error) {
      console.error(`[StorageManager] Error getting item "${key}":`, error)
      return null
    }
  }

  /**
   * Сохранить значение в хранилище
   * @param {string} key - Ключ
   * @param {string} value - Значение (должно быть строка)
   * @returns {Promise<boolean>} - Успешно ли выполнено
   */
  static async setItem(key, value) {
    try {
      await Preferences.set({ key, value: String(value) })
      return true
    } catch (error) {
      console.error(`[StorageManager] Error setting item "${key}":`, error)
      return false
    }
  }

  /**
   * Удалить значение из хранилища
   * @param {string} key - Ключ
   * @returns {Promise<boolean>} - Успешно ли выполнено
   */
  static async removeItem(key) {
    try {
      await Preferences.remove({ key })
      return true
    } catch (error) {
      console.error(`[StorageManager] Error removing item "${key}":`, error)
      return false
    }
  }

  /**
   * Очистить все хранилище
   * @returns {Promise<boolean>} - Успешно ли выполнено
   */
  static async clear() {
    try {
      await Preferences.clear()
      return true
    } catch (error) {
      console.error('[StorageManager] Error clearing storage:', error)
      return false
    }
  }

  /**
   * Получить все ключи из хранилища
   * @returns {Promise<string[]>} - Массив ключей
   */
  static async keys() {
    try {
      const { keys } = await Preferences.keys()
      return keys || []
    } catch (error) {
      console.error('[StorageManager] Error getting keys:', error)
      return []
    }
  }
}

export default StorageManager
