<template>

<ion-page>
    <ion-content 
      :fullscreen="true"
      class="ion-content-center"
      :style="{ '--background': 'linear-gradient(to bottom right, #f1f5f9, #e0f2fe)' }"
    >
      <!-- Card Container - Centered -->
      <div class="login-container">
        <div class="login-card">
          <!-- Title -->
          <h1 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">
            Вход в систему учёта ГСМ ПСЧ МЧС 37
          </h1>

          <!-- Description -->
          <p class="text-sm mb-6" :style="{ color: palette.medium }">
            Пожалуйста, введите логин и пароль для доступа.
          </p>

          <!-- Error Alert -->
          <div v-if="error" class="mb-6 p-4 rounded-lg" :style="{ backgroundColor: palette.error + '20', borderLeft: `4px solid ${palette.error}` }">
            <p class="text-sm" :style="{ color: palette.error }">{{ error }}</p>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="space-y-4 w-full">
            <!-- Login Input -->
            <div>
              <label class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">Логин</label>
              <input
                v-model="form.login"
                type="text"
                placeholder="Введите логин"
                required
                class="w-full px-4 py-2 rounded-lg border outline-none transition focus:ring-2"
                :style="{ 
                  color: palette.dark,
                  borderColor: palette.light,
                  backgroundColor: '#ffffff',
                  '--tw-ring-color': palette.primary + '40'
                }"
              />
            </div>

            <!-- Password Input -->
            <div>
              <label class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">Пароль</label>
              <div class="relative">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  v-model="form.password"
                  placeholder="Введите пароль"
                  autocomplete="current-password"
                  required
                  class="w-full px-4 py-2 rounded-lg border outline-none transition focus:ring-2"
                  :style="{ 
                    color: palette.dark,
                    borderColor: palette.light,
                    backgroundColor: '#ffffff',
                    '--tw-ring-color': palette.primary + '40'
                  }"
                />

                <!-- Password Toggle Button -->
                <button
                  type="button"
                  @click="toggleShowPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-800"
                  :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                >
                  <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 3C5 3 1.73 7.11 1 10c.73 2.89 4 7 9 7s8.27-4.11 9-7c-.73-2.89-4-7-9-7zM10 14a4 4 0 110-8 4 4 0 010 8z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0110 19c-5 0-8.27-4.11-9-7a14.96 14.96 0 012.36-3.91M3 3l18 18" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.88 9.88A3 3 0 0114.12 14.12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Submit Button -->
            <div class="pt-4">
              <Button
                label="Войти"
                variant="primary"
                type="submit"
                expand="block"
                :disabled="isLoading"
                :is-loading="isLoading"
                loading-text="Вход..."
              />
            </div>
          </form>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonContent,
} from '@ionic/vue'
import { palette, Button } from '@/components/ui/importUi'
import { api } from '@/api'
import { getErrorMessage } from '@/utils'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const router = useRouter()

const form = ref({
  login: '',
  password: '',
})

const showPassword = ref(false)
const isLoading = ref(false)
const error = ref('')

const toggleShowPassword = () => {
  showPassword.value = !showPassword.value
}

const handleSubmit = async () => {
  error.value = ''

  // Валидация
  if (!form.value.login || !form.value.password) {
    error.value = 'Введите логин и пароль'
    return
  }

  const loginClean = form.value.login.trim()
  const passwordClean = form.value.password.trim()

  if (/\s/.test(passwordClean)) {
    error.value = 'Пароль не должен содержать пробелы'
    return
  }

  isLoading.value = true

  try {
    const response = await api.auth.login(loginClean, passwordClean)

    if (response.data.access) {
      // Сохраняем токен и пользователя в localStorage для офлайн режима
      localStorage.setItem('auth_token', response.data.access)
      localStorage.setItem('auth_user', JSON.stringify(response.data.user))
      authStore.setUser(response.data.user)
      authStore.setToken(response.data.access)
      router.push('/waybills')
    } else {
      error.value = 'Неверный логин или пароль'
    }
  } catch (err) {
    error.value = getErrorMessage(err)
    console.error('[LoginPage] Error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.ion-content-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  min-height: 100vh;
}

.login-card {
  width: 100%;
  max-width: 28rem;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}
</style>