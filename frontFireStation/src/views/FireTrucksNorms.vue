<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Нормы для пожарных автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите данные для поиска" class="mb-4" />
        <DataTable :data="filteredNorms" :columns="columns" @row-click="openEditModal" />
      </div>
    </div>

    <!-- Edit Norm Modal -->
    <Modal :is-open="isEditModalOpen" title="Редактировать норму" @close="closeEditModal">
      <form @submit.prevent="saveNorm">
        <TextInput v-model="editableNorm.season" label="Сезон" required />
        <TextInput v-model="editableNorm.city_norm" label="Городская норма (л/км)" required />
        <TextInput v-model="editableNorm.area_norm" label="Областная норма (л/км)" required />
        <TextInput v-model="editableNorm.date" label="Дата утверждения" required type="date" />
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
const norms = ref([]);
const searchQuery = ref('');
const isEditModalOpen = ref(false);
const editableNorm = ref({});

const columns = [
  { key: 'season', label: 'Сезон' },
  { key: 'city_norm', label: 'Городская норма (л/км)' },
  { key: 'area_norm', label: 'Областная норма (л/км)' },
  { key: 'date', label: 'Дата утверждения' }
];

const fetchNorms = async () => {
  try {
    const response = await axios.get('/fire-truck-norms/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    norms.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке норм:', error);
  }
};

const filteredNorms = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return norms.value.filter(norm =>
    norm.season.toLowerCase().includes(query) ||
    norm.city_norm.toString().includes(query) ||
    norm.area_norm.toString().includes(query) ||
    norm.date.includes(query)
  );
});

const openEditModal = (norm) => {
  editableNorm.value = { ...norm };
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
};

const saveNorm = async () => {
  try {
    await axios.put(`/api/fire-truck-norms/${editableNorm.value.id}/`, editableNorm.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchNorms();
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных:', error);
  }
};

onMounted(fetchNorms);
</script>
