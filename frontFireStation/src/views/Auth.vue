<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col">


    <main class="flex-1 flex items-center justify-center px-4 py-12">
      <div class="w-full max-w-md bg-white rounded-lg shadow p-8" :style="{ borderColor: palette.light }">
        <h1 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Вход в систему учёта ГСМ ПСЧ МЧС 37</h1>
        <p class="text-sm mb-6" :style="{ color: palette.medium }">Пожалуйста, введите логин и пароль для доступа.</p>

        <form @submit.prevent="submit" class="space-y-4">
          <TextInput
            v-model="login"
            label="Логин"
            placeholder="Введите логин"
            required
          />

          <div>
            <label class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">Пароль</label>
            <div class="relative">
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="password"
                autocomplete="current-password"
                required
                :style="passwordInputStyle"
                class="w-full px-4 py-2 rounded-lg outline-none transition"
                placeholder="Введите пароль"
              />

              <button
                type="button"
                @click="toggleShowPassword"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-gray-600 hover:text-gray-800"
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

          <div class="flex items-center justify-between">
            <div class="text-sm" :style="{ color: palette.medium }">&nbsp;</div>
            <Button type="submit" variant="primary" label="Войти" />
          </div>
        </form>

        <p v-if="error" class="mt-4 text-sm" :style="{ color: palette.error }">{{ error }}</p>
      </div>
    </main>

  
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import HeaderComponent from '../components/HeaderComponent.vue';
import FooterComponent from '../components/FooterComponent.vue';
import { TextInput, Button, palette } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();

const login = ref('');
const password = ref('');
const showPassword = ref(false);
const error = ref('');

function toggleShowPassword() {
  showPassword.value = !showPassword.value;
}

const passwordInputStyle = computed(() => ({
  color: palette.dark,
  borderColor: palette.light,
  backgroundColor: 'white',
  border: `1px solid ${palette.light}`,
}));

async function submit() {
  error.value = '';
  if (!login.value || !password.value) {
    error.value = 'Введите логин и пароль';
    return;
  }

  try {
    const ok = await auth.login(login.value, password.value);
    if (ok) {
      router.push('/fuel-report');
    } else {
      error.value = 'Неверный логин или пароль';
    }
  } catch (e) {
    error.value = 'Ошибка при подключении';
  }
}
</script>
