<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Пользователи</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите ФИО, логин или телефон" class="mb-4" />
        <DataTable :data="filteredUsers" :columns="columns" @row-click="viewUserDetails">
        </DataTable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { DataTable, TextInput, palette } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';

const auth = useAuthStore();
const users = ref([]);
const searchQuery = ref('');

const columns = [
  { key: 'name', label: 'Имя' },
  { key: 'surname', label: 'Фамилия' },
  { key: 'last_name', label: 'Отчество' },
  { key: 'login', label: 'Логин' },
  { key: 'phone', label: 'Телефон' }
];

const fetchUsers = async () => {
  // Проверяем разрешение view_users
  if (!auth.permissions.view_users) {
    console.warn('Нет разрешения на просмотр пользователей (view_users).');
    return;
  }

  try {
    // Получаем всех пользователей
    const response = await axios.get('/users/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    users.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке пользователей:', error);
  }
};

const filteredUsers = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return users.value.filter(user =>
    user.name.toLowerCase().includes(query) ||
    user.surname.toLowerCase().includes(query) ||
    user.last_name.toLowerCase().includes(query) ||
    user.login.toLowerCase().includes(query) ||
    user.phone.includes(query)
  );
});

const viewUserDetails = (user) => {
  console.log('Просмотр деталей пользователя:', user);
};

/**
 * Установить CRUD разрешения для этой страницы на основе разрешений пользователя
 */
const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_users || false,
    canDelete: auth.permissions.can_delete_users || false,
  });
};

onMounted(() => {
  console.debug("[Users] Permissions loaded from store:", auth.permissions);
  setupCrudPermissions();
  
  if (auth.permissions.view_users) {
    fetchUsers();
  } else {
    console.warn("[Users] User does not have permission to view users.");
  }
});

onUnmounted(() => {
  // Очистить CRUD разрешения при выходе со страницы
  auth.clearCrudPermissions();
});
</script>
