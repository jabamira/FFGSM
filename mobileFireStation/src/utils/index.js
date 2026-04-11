export const formatDate = (date, format = 'DD.MM.YYYY') => {
  const d = typeof date === 'string' ? new Date(date) : date

  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()

  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')

  return format
    .replace('DD', day)
    .replace('MM', month)
    .replace('YYYY', String(year))
    .replace('HH', hours)
    .replace('MM', minutes)
}

export const getDaysDifference = (date1, date2) => {
  const d1 = typeof date1 === 'string' ? new Date(date1) : date1
  const d2 = typeof date2 === 'string' ? new Date(date2) : date2
  const diffTime = Math.abs(d2.getTime() - d1.getTime())
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

export const toISODate = (date) => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toISOString().split('T')[0]
}

/**
 * Получает дату в часовом поясе Новосибирска (UTC+7)
 * @param {Date} date - дата (если не передана, используется текущая)
 * @returns {string} дата в формате YYYY-MM-DD
 */
export const getNovosibirskDate = (date = new Date()) => {
  const d = typeof date === 'string' ? new Date(date) : date
  // Смещение UTC+7 для Новосибирска (в миллисекундах)
  const offset = 7 * 60 * 60 * 1000
  const novosibirskDate = new Date(d.getTime() + offset)
  return novosibirskDate.toISOString().split('T')[0]
}

export const getToday = () => {
  return getNovosibirskDate()
}

export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }

  if (error.response?.data?.message) {
    return error.response.data.message
  }

  if (error.message) {
    return error.message
  }

  return 'Произошла ошибка. Пожалуйста, попробуйте позже.'
}

export const getFormErrors = (error) => {
  if (error.response?.data && typeof error.response.data === 'object') {
    return error.response.data
  }

  return {}
}

export const isNetworkError = (error) => {
  return !error.response
}

export const isAuthError = (error) => {
  return error.response?.status === 401
}

export const isPermissionError = (error) => {
  return error.response?.status === 403
}

export const isValidationError = (error) => {
  return error.response?.status === 400
}
