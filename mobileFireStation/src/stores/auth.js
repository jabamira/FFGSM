import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  const setUser = (newUser) => {
    user.value = newUser
  }

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('auth_token', newToken)
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
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
  }
})
