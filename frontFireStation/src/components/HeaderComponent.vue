<template>
  <nav :style="{ background: palette.white, borderBottom: `1px solid ${palette.light}` }" class="fixed top-0 left-0 w-full z-50 p-3">
    <div class="max-w-7xl mx-auto flex items-center gap-4">
      <!-- Логотип МЧС -->
      <a @click="nav.NavigateHome()" class="flex items-center gap-3 cursor-pointer">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle :fill="palette.primary" cx="24" cy="24" r="22" />
          <text x="24" y="30" text-anchor="middle" :style="{ fill: palette.white, fontWeight: '700', fontSize: '14px' }">ПСЧ</text>
        </svg>
        <div>
          <div :style="{ color: palette.dark, fontWeight: 700 }">ПСЧ МЧС 37</div>
          <div class="text-sm" :style="{ color: palette.medium }">Пожарно-спасательный отряд</div>
        </div>
      </a>

      <div class="ml-auto flex items-center gap-3">
        <!-- Кнопка входа -->
        <a v-if="!authStore.isAuthenticated && route.path !== '/auth'" href="#/auth?mode=login" :style="loginButtonStyle" class="px-3 py-1.5 rounded text-sm font-medium">Войти</a>

        <!-- Профиль пользователя -->
        <div v-if="authStore.isAuthenticated" class="relative">
          <button
            @click="toggleDropdown"
            ref="avatarButton"
            class="flex items-center justify-center h-10 w-10 rounded-full overflow-hidden"
            :style="{ border: `1px solid ${palette.light}` }"
          >
            <img
              :src="avatarSrc"
              alt="User"
              class="h-10 w-10 object-cover object-center rounded-full"
            />
          </button>

          <!-- Dropdown -->
          <div
            v-show="dropdownOpen"
            class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
          >
            <div class="px-4 py-2 text-sm" :style="{ color: palette.dark }">
              <div class="font-medium">{{ authStore.user?.login }}</div>
              <div class="text-xs" :style="{ color: palette.medium }">{{ authStore.user?.email }}</div>
            </div>
            <ul class="py-2 text-sm">
              <li>
                <a @click="nav.NavigateUser" class="block px-4 py-2 hover:bg-gray-100 cursor-pointer">Профиль</a>
              </li>
              <li>
                <a @click="logout" class="block px-4 py-2 hover:bg-gray-100 cursor-pointer">Выйти</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useNavigation } from "../router/navigation.js";
import { useAuthStore } from "../stores/auth";
import { palette } from './ui/theme.js';

const router = useRouter();
const route = useRoute();
const nav = useNavigation();
const authStore = useAuthStore();

// Dropdown
const dropdownOpen = ref(false);
const avatarButton = ref(null);

// Аватар
const avatarSrc = ref(
  authStore.user?.avatarUrl
    ? `http://localhost:3000${authStore.user.avatarUrl}`
    : "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/helene-engels.png"
);

// Слежение за изменением пользователя и аватара
watch(
  () => authStore.user,
  (newUser) => {
    avatarSrc.value = newUser?.avatarUrl
      ? `http://localhost:3000${newUser.avatarUrl}`
      : "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/helene-engels.png";
  },
  { immediate: true }
);

// Переключение dropdown
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}

// Выход
async function logout() {
  await authStore.logout();
  dropdownOpen.value = false;
  avatarSrc.value = "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/helene-engels.png";
  router.push("/auth");
}

// Закрытие dropdown при клике вне
function handleClickOutside(event) {
  if (avatarButton.value && !avatarButton.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

const loginButtonStyle = computed(() => ({
  backgroundColor: palette.primary,
  color: palette.white,
  border: `1px solid ${palette.primary}`,
}));
</script>

<style scoped>
button img {
  display: block;
}
</style>
