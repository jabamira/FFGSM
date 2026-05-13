/**
 * Система синхронизации данных для оффлайн режима
 */

import StorageManager from './storageManager'

export const SYNC_QUEUE = {
  WAYBILL_UPDATE: 'sync_waybill_update',
  WAYBILL_RECORD_CREATE: 'sync_waybill_record_create',
  TRIP_START: 'sync_trip_start',
  TRIP_END: 'sync_trip_end',
}

/**
 * Добавляет операцию в очередь синхронизации
 */
export const addSyncOperation = async (type, data) => {
  try {
    const queueData = await StorageManager.getItem('sync_queue')
    const queue = queueData ? JSON.parse(queueData) : []
    queue.push({
      id: Date.now(),
      type,
      data,
      timestamp: Date.now(),
      status: 'pending', // pending, syncing, completed, failed
    })
    await StorageManager.setItem('sync_queue', JSON.stringify(queue))
    return true
  } catch (err) {
    console.error('[SyncQueue] Error adding operation:', err)
    return false
  }
}

/**
 * Получает все операции из очереди
 */
export const getSyncQueue = async () => {
  try {
    const queueData = await StorageManager.getItem('sync_queue')
    return queueData ? JSON.parse(queueData) : []
  } catch (err) {
    console.error('[SyncQueue] Error getting queue:', err)
    return []
  }
}

/**
 * Удаляет операцию из очереди
 */
export const removeSyncOperation = async (operationId) => {
  try {
    const queue = await getSyncQueue()
    const filtered = queue.filter(op => op.id !== operationId)
    await StorageManager.setItem('sync_queue', JSON.stringify(filtered))
    return true
  } catch (err) {
    console.error('[SyncQueue] Error removing operation:', err)
    return false
  }
}

/**
 * Обновляет статус операции
 */
export const updateSyncOperationStatus = async (operationId, status) => {
  try {
    const queue = await getSyncQueue()
    const operation = queue.find(op => op.id === operationId)
    if (operation) {
      operation.status = status
      operation.lastAttempt = Date.now()
    }
    await StorageManager.setItem('sync_queue', JSON.stringify(queue))
    return true
  } catch (err) {
    console.error('[SyncQueue] Error updating status:', err)
    return false
  }
}

/**
 * Очищает очередь синхронизации
 */
export const clearSyncQueue = async () => {
  try {
    await StorageManager.removeItem('sync_queue')
    return true
  } catch (err) {
    console.error('[SyncQueue] Error clearing queue:', err)
    return false
  }
}

/**
 * Получает количество ожидающих синхронизации
 */
export const getPendingSyncCount = async () => {
  const queue = await getSyncQueue()
  return queue.filter(op => op.status === 'pending' || op.status === 'failed').length
}

export default {
  addSyncOperation,
  getSyncQueue,
  removeSyncOperation,
  updateSyncOperationStatus,
  clearSyncQueue,
  getPendingSyncCount,
  SYNC_QUEUE,
}
