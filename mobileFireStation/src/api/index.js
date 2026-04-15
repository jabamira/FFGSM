import apiClient from './client'

export const authApi = {
  login: (login, password) =>
    apiClient.post('/auth/login/', { login, password, client: 'mobile' }),

  logout: () =>
    apiClient.post('/auth/logout/'),

  getProfile: () =>
    apiClient.get('/auth/profile/'),

  updateProfile: (data) =>
    apiClient.patch('/auth/profile/', data),
}

export const waybillApi = {
  // Получает пассажирские путевые листы
  listPassengerCar: (params) =>
    apiClient.get('/passenger-car-waybills/', { params }),

  getPassengerCar: (id) =>
    apiClient.get(`/passenger-car-waybills/${id}/`),

  createPassengerCar: (data) =>
    apiClient.post('/passenger-car-waybills/', data),

  updatePassengerCar: (id, data) =>
    apiClient.put(`/passenger-car-waybills/${id}/`, data),

  deletePassengerCar: (id) =>
    apiClient.delete(`/passenger-car-waybills/${id}/`),

  completePassengerCar: (id) =>
    apiClient.post(`/passenger-car-waybills/${id}/complete/`),

  listFireTruck: (params) =>
    apiClient.get('/fire-truck-waybills/', { params }),

  getFireTruck: (id) =>
    apiClient.get(`/fire-truck-waybills/${id}/`),

  createFireTruck: (data) =>
    apiClient.post('/fire-truck-waybills/', data),

  updateFireTruck: (id, data) =>
    apiClient.put(`/fire-truck-waybills/${id}/`, data),

  deleteFireTruck: (id) =>
    apiClient.delete(`/fire-truck-waybills/${id}/`),

  completeFireTruck: (id) =>
    apiClient.post(`/fire-truck-waybills/${id}/complete/`),

  // Объединённая функция для получения всех путевых листов текущего водителя
  list: async (params) => {
    try {
      const [passengerRes, fireTruckRes] = await Promise.all([
        apiClient.get('/passenger-car-waybills/', { params }),
        apiClient.get('/fire-truck-waybills/', { params }),
      ])
      
      const passengerData = passengerRes.data.results || passengerRes.data || []
      const fireTruckData = fireTruckRes.data.results || fireTruckRes.data || []
      
      // Объединяем данные
      const combined = [
        ...passengerData,
        ...fireTruckData,
      ]
      
      return {
        data: combined.sort((a, b) => new Date(b.date) - new Date(a.date))
      }
    } catch (err) {
      console.error('[WaybillApi] Error listing waybills:', err)
      throw err
    }
  },

  // Получить путевой лист по ID (нужно знать тип)
  get: async (id, type = 'passenger_car') => {
    if (type === 'fire_truck') {
      return apiClient.get(`/fire-truck-waybills/${id}/`)
    }
    return apiClient.get(`/passenger-car-waybills/${id}/`)
  },

  // Завершить путевой лист
  complete: async (id, type = 'passenger_car') => {
    if (type === 'fire_truck') {
      return apiClient.post(`/fire-truck-waybills/${id}/complete/`)
    }
    return apiClient.post(`/passenger-car-waybills/${id}/complete/`)
  },
}

export const fuelApi = {
  list: (params) =>
    apiClient.get('/fuel-reports/', { params }),

  create: (data) =>
    apiClient.post('/fuel-reports/', data),

  update: (id, data) =>
    apiClient.put(`/fuel-reports/${id}/`, data),

  delete: (id) =>
    apiClient.delete(`/fuel-reports/${id}/`),
}

export const vehicleApi = {
  list: (params) =>
    apiClient.get('/vehicles/', { params }),

  get: (id) =>
    apiClient.get(`/vehicles/${id}/`),

  getMaintenance: (id) =>
    apiClient.get(`/vehicles/${id}/maintenance/`),
}

export const reportApi = {
  getStatistics: (params) =>
    apiClient.get('/reports/statistics/', { params }),

  getFuelReport: (params) =>
    apiClient.get('/reports/fuel/', { params }),
}

export const api = {
  auth: authApi,
  waybill: waybillApi,
  fuel: fuelApi,
  vehicle: vehicleApi,
  report: reportApi,
  client: apiClient,
}

export default api
