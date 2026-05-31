import axios from 'axios'
import StorageManager from '../utils/storageManager'

class ApiClient {
  constructor(baseURL = 'http://192.168.1.199:8000/api') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Интерцептор для добавления токена (асинхронный)
    this.client.interceptors.request.use(async (config) => {
      console.log('[API Request] Sending:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        fullURL: config.baseURL + config.url,
        data: config.data ? (typeof config.data === 'string' ? config.data : JSON.stringify(config.data)) : null,
        timeout: config.timeout,
      })
      const token = await StorageManager.getItem('auth_token')
      if (token) {
        console.log('[API Request] Token attached:', token.substring(0, 20) + '...')
        config.headers.Authorization = `Bearer ${token}`
      } else {
        console.warn('[API Request] No token found in storage')
      }
      return config
    }, (error) => {
      console.error('[API Request Interceptor Error]', error)
      return Promise.reject(error)
    })

    // Интерцептор для обработки ошибок
    this.client.interceptors.response.use(
      (response) => {
        console.log('[API Response] Received:', {
          status: response.status,
          url: response.config.url,
          data: response.data,
        })
        return response
      },
      async (error) => {
        console.error('[API Error Response]', {
          message: error.message,
          code: error.code,
          status: error.response?.status,
          data: error.response?.data,
          config: {
            url: error.config?.url,
            method: error.config?.method,
          },
        })
        
        // Если токен истек или доступ запрещен (401 или 403)
        if (error.response?.status === 401 || error.response?.status === 403) {
          console.warn('[API] Unauthorized (401/403) - clearing auth and redirecting to login')
          
          // Очищаем storage
          await StorageManager.removeItem('auth_token')
          await StorageManager.removeItem('auth_user')
          
          // Очищаем Pinia store если он инициализирован
          try {
            const { useAuthStore } = await import('../stores/auth')
            const authStore = useAuthStore()
            authStore.logout()
            console.log('[API] Auth store cleared')
          } catch (err) {
            console.warn('[API] Could not clear auth store:', err)
          }
          
          // Только если не на странице логина
          if (window.location.pathname !== '/login') {
            console.log('[API] Redirecting to login page')
            window.location.href = '/login'
          }
        }
        
        return Promise.reject(error)
      }
    )
  }

  get(url, config) {
    return this.client.get(url, config)
  }

  post(url, data, config) {
    return this.client.post(url, data, config)
  }

  put(url, data, config) {
    return this.client.put(url, data, config)
  }

  patch(url, data, config) {
    return this.client.patch(url, data, config)
  }

  delete(url, config) {
    return this.client.delete(url, config)
  }
}

export default new ApiClient()
