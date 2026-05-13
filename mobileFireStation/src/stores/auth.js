import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import StorageManager from '../utils/storageManager'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  const setUser = (newUser) => {
    user.value = newUser
  }

  const setToken = async (newToken) => {
    token.value = newToken
    await StorageManager.setItem('auth_token', newToken)
  }

  const logout = async () => {
    user.value = null
    token.value = null
    await StorageManager.removeItem('auth_token')
    await StorageManager.removeItem('auth_user')
  }

  const loadToken = async () => {
    const savedToken = await StorageManager.getItem('auth_token')
    if (savedToken) {
      token.value = savedToken
    }
    return savedToken
  }

  const saveUser = async (userData) => {
    user.value = userData
    await StorageManager.setItem('auth_user', JSON.stringify(userData))
  }

  const loadUser = async () => {
    const savedUser = await StorageManager.getItem('auth_user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
    return savedUser
  }

  const setError = (newError) => {
    error.value = newError
  }

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    setUser,
    setToken,
    logout,
    setError,
    setLoading,
    loadToken,
    saveUser,
    loadUser,
  }
})
