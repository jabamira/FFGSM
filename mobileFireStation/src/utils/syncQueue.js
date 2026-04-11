/**
 * Система синхронизации данных для оффлайн режима
 */

export const SYNC_QUEUE = {
  WAYBILL_UPDATE: 'sync_waybill_update',
  WAYBILL_RECORD_CREATE: 'sync_waybill_record_create',
}

/**
 * Добавляет операцию в очередь синхронизации
 */
export const addSyncOperation = (type, data) => {
  try {
    const queue = JSON.parse(localStorage.getItem('sync_queue') || '[]')
    queue.push({
      id: Date.now(),
      type,
      data,
      timestamp: Date.now(),
      status: 'pending', // pending, syncing, completed, failed
    })
    localStorage.setItem('sync_queue', JSON.stringify(queue))
    return true
  } catch (err) {
    console.error('[SyncQueue] Error adding operation:', err)
    return false
  }
}

/**
 * Получает все операции из очереди
 */
export const getSyncQueue = () => {
  try {
    return JSON.parse(localStorage.getItem('sync_queue') || '[]')
  } catch (err) {
    console.error('[SyncQueue] Error getting queue:', err)
    return []
  }
}

/**
 * Удаляет операцию из очереди
 */
export const removeSyncOperation = (operationId) => {
  try {
    const queue = getSyncQueue()
    const filtered = queue.filter(op => op.id !== operationId)
    localStorage.setItem('sync_queue', JSON.stringify(filtered))
    return true
  } catch (err) {
    console.error('[SyncQueue] Error removing operation:', err)
    return false
  }
}

/**
 * Обновляет статус операции
 */
export const updateSyncOperationStatus = (operationId, status) => {
  try {
    const queue = getSyncQueue()
    const operation = queue.find(op => op.id === operationId)
    if (operation) {
      operation.status = status
      operation.lastAttempt = Date.now()
    }
    localStorage.setItem('sync_queue', JSON.stringify(queue))
    return true
  } catch (err) {
    console.error('[SyncQueue] Error updating status:', err)
    return false
  }
}

/**
 * Очищает очередь синхронизации
 */
export const clearSyncQueue = () => {
  try {
    localStorage.removeItem('sync_queue')
    return true
  } catch (err) {
    console.error('[SyncQueue] Error clearing queue:', err)
    return false
  }
}

/**
 * Получает количество ожидающих синхронизации
 */
export const getPendingSyncCount = () => {
  const queue = getSyncQueue()
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
