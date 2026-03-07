<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Водители</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите ФИО, телефон или удостоверение" class="mb-4" />
        <DataTable :data="filteredDrivers" :columns="columns" @row-click="viewDriverDetails">
        </DataTable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { DataTable, TextInput, palette } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';

const auth = useAuthStore();
const drivers = ref([]);
const searchQuery = ref('');

const columns = [
  { key: 'name', label: 'Имя' },
  { key: 'surname', label: 'Фамилия' },
  { key: 'last_name', label: 'Отчество' },
  { key: 'phone', label: 'Телефон' },
  { key: 'driver_license', label: 'Водительское удостоверение' }
];

const fetchDrivers = async () => {
  try {
    const response = await axios.get('users/?role=3', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    drivers.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке водителей:', error);
  }
};

const filteredDrivers = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return drivers.value.filter(driver =>
    driver.name.toLowerCase().includes(query) ||
    driver.surname.toLowerCase().includes(query) ||
    driver.last_name.toLowerCase().includes(query) ||
    driver.phone.includes(query) ||
    (driver.driver_license && driver.driver_license.includes(query))
  );
});

const viewDriverDetails = (driver) => {
  console.log('Просмотр деталей водителя:', driver);
};

onMounted(fetchDrivers);
</script>
