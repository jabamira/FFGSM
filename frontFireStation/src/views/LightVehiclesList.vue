<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Список легковых автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите данные для поиска" class="mb-4" />
        <DataTable :data="filteredPassengerCars" :columns="columns" @row-click="openEditModal" />
      </div>
    </div>

    <!-- Edit Passenger Car Modal -->
    <Modal :is-open="isEditModalOpen" title="Редактировать данные" @close="closeEditModal">
      <form @submit.prevent="savePassengerCar">
        <TextInput v-model="editablePassengerCar.number" label="Гос. номер" required />
        <TextInput v-model="editablePassengerCar.brand" label="Марка" required />
        <TextInput v-model="editablePassengerCar.model" label="Модель" required />
        <Button label="Сохранить" variant="primary" type="submit" />
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { DataTable, TextInput, Modal, Button, palette } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';

const auth = useAuthStore();
const passengerCars = ref([]);
const searchQuery = ref('');
const isEditModalOpen = ref(false);
const editablePassengerCar = ref({});

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' }
];

const fetchPassengerCars = async () => {
  try {
    const response = await axios.get('/passenger-cars/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    passengerCars.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке легковых автомобилей:', error);
  }
};

const filteredPassengerCars = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return passengerCars.value.filter(car =>
    car.number.toLowerCase().includes(query) ||
    car.brand.toLowerCase().includes(query) ||
    car.model.toLowerCase().includes(query)
  );
});

const openEditModal = (car) => {
  editablePassengerCar.value = { ...car };
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
};

const savePassengerCar = async () => {
  try {
    await axios.put(`/api/passenger-cars/${editablePassengerCar.value.id}/`, editablePassengerCar.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchPassengerCars();
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных:', error);
  }
};

onMounted(fetchPassengerCars);
</script>
