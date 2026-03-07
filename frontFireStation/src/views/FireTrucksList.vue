<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Список пожарных автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите данные для поиска" class="mb-4" />
        <DataTable :data="filteredFireTrucks" :columns="columns" @row-click="openEditModal" />
      </div>
    </div>

    <!-- Edit Fire Truck Modal -->
    <Modal :is-open="isEditModalOpen" title="Редактировать данные" @close="closeEditModal">
      <form @submit.prevent="saveFireTruck">
        <TextInput v-model="editableFireTruck.number" label="Гос. номер" required />
        <TextInput v-model="editableFireTruck.brand" label="Марка" required />
        <TextInput v-model="editableFireTruck.model" label="Модель" required />
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
const fireTrucks = ref([]);
const searchQuery = ref('');
const isEditModalOpen = ref(false);
const editableFireTruck = ref({});

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' }
];

const fetchFireTrucks = async () => {
  try {
    const response = await axios.get('/fire-trucks/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fireTrucks.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке пожарных автомобилей:', error);
  }
};

const filteredFireTrucks = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return fireTrucks.value.filter(truck =>
    truck.number.toLowerCase().includes(query) ||
    truck.brand.toLowerCase().includes(query) ||
    truck.model.toLowerCase().includes(query)
  );
});

const openEditModal = (truck) => {
  editableFireTruck.value = { ...truck };
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
};

const saveFireTruck = async () => {
  try {
    await axios.put(`/api/fire-trucks/${editableFireTruck.value.id}/`, editableFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchFireTrucks();
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных:', error);
  }
};

onMounted(fetchFireTrucks);
</script>
