<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Нормы для легковых автомобилей</h2>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div class="bg-white rounded shadow p-4">
          <label class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">Автомобиль</label>
          <SelectInput
            v-model="filterCar"
            :options="carsFilterOptions"
            placeholder="Все автомобили"
          />
        </div>
        <div class="bg-white rounded shadow p-4">
          <label class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">Сезон</label>
          <SelectInput
            v-model="filterSeason"
            :options="[
              { value: '', label: 'Все сезоны' },
              { value: 'summer', label: 'Лето' },
              { value: 'winter', label: 'Зима' }
            ]"
            placeholder="Все сезоны"
          />
        </div>
      </div>

      <!-- Search and Info -->
      <div class="flex justify-between items-center mb-4">
        <div class="flex-1 max-w-md">
          <TextInput
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по ID норм..."
          />
        </div>
        <span class="text-sm" :style="{ color: palette.medium }">Всего: {{ filteredNorms.length }}</span>
      </div>

      <!-- DataTable -->
      <div class="bg-white rounded shadow overflow-hidden mb-16">
        <DataTable
          :columns="columns"
          :data="filteredNorms"
          :selectedIds="selectedNormIds"
          @select="(ids) => selectedNormIds = ids"
          :hideActions="true"
        >
          <template #cell-car="{ row }">
            {{ getCar(row.car_id)?.number || '-' }} ({{ getCar(row.car_id)?.brand }} {{ getCar(row.car_id)?.model }})
          </template>
          <template #cell-season="{ row }">
            {{ row.season === 'summer' ? 'Лето' : 'Зима' }}
          </template>
          <template #cell-city_norm="{ row }">
            {{ row.city_norm }} л/100км
          </template>
          <template #cell-area_norm="{ row }">
            {{ row.area_norm }} л/100км
          </template>
          <template #cell-date="{ row }">
            {{ row.date ? formatDate(row.date) : '-' }}
          </template>
          <template #actions="{ row }">
            <button
              @click="openEditNormModal(row)"
              class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 mr-2"
            >
              Редактировать
            </button>
          </template>
        </DataTable>
      </div>

      <!-- Edit Modals Component -->
      <NormEditModal
        ref="normModal"
        :carOptions="carOptions"
        @add="handleAddNorm"
        @edit="handleEditNorm"
        @delete="handleDeleteNorms"
      />

      <!-- CRUD Panel -->
      <CrudPanel
        :canCreate="auth.permissions.can_create_passenger_car_norms"
        :canDelete="auth.permissions.can_delete_passenger_car_norms && selectedNormIds.length > 0"
        createLabel="Создать норму"
        :deleteLabel="`Удалить норм (${selectedNormIds.length})`"
        @create="openAddNormModal"
        @delete="openDeleteNormModal"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { palette, SelectInput, TextInput } from '../components/ui/importUi';
import CrudPanel from '../components/CrudPanel.vue';
import DataTable from '../components/ui/DataTable.vue';
import NavigationMenu from '../components/NavigationMenu.vue';
import NormEditModal from '../components/NormEditModal.vue';
import axios from 'axios';

const auth = useAuthStore();

// Data
const norms = ref([]);
const passengerCars = ref([]);

// Selection and Modals
const selectedNormIds = ref([]);
const normModal = ref(null);

// Filters
const searchQuery = ref('');
const filterCar = ref('');
const filterSeason = ref('');

// Computed
const carOptions = computed(() => {
  return passengerCars.value.map(car => ({
    value: car.id,
    label: `${car.number} - ${car.brand} ${car.model}`
  }));
});

const carsFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все автомобили' },
    ...passengerCars.value.map(car => ({
      value: car.id,
      label: `${car.number} - ${car.brand} ${car.model}`
    }))
  ];
});

const filteredNorms = computed(() => {
  let filtered = norms.value;

  if (searchQuery.value) {
    filtered = filtered.filter(n => 
      n.id.toString().includes(searchQuery.value)
    );
  }

  if (filterCar.value) {
    filtered = filtered.filter(n => n.car_id === parseInt(filterCar.value));
  }

  if (filterSeason.value) {
    filtered = filtered.filter(n => n.season === filterSeason.value);
  }

  return filtered;
});

const columns = computed(() => [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'car', label: 'Автомобиль', sortable: false },
  { key: 'season', label: 'Сезон', sortable: true },
  { key: 'city_norm', label: 'Норма город', sortable: true },
  { key: 'area_norm', label: 'Норма трасса', sortable: true },
  { key: 'date', label: 'Дата', sortable: true }
]);

// Methods
const getCar = (carId) => {
  return passengerCars.value.find(c => c.id === carId);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU');
};

const openAddNormModal = () => {
  normModal.value?.openAddModal();
};

const openDeleteNormModal = () => {
  normModal.value?.openDeleteModal(selectedNormIds.value.length);
};

const openEditNormModal = (norm) => {
  normModal.value?.openEditModal(norm);
};

const handleAddNorm = async (normData) => {
  try {
    await axios.post('passenger-car-norms/', normData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    await fetchNorms();
  } catch (error) {
    normModal.value?.showError(
      'Ошибка создания норм',
      error.response?.data?.detail || 'Произошла ошибка при создании норм'
    );
  }
};

const handleEditNorm = async (normData) => {
  try {
    await axios.patch(`passenger-car-norms/${normData.id}/`, normData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    await fetchNorms();
  } catch (error) {
    normModal.value?.showError(
      'Ошибка обновления норм',
      error.response?.data?.detail || 'Произошла ошибка при обновлении норм'
    );
  }
};

const handleDeleteNorms = async () => {
  try {
    for (const id of selectedNormIds.value) {
      await axios.delete(`passenger-car-norms/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    await fetchNorms();
    selectedNormIds.value = [];
  } catch (error) {
    if (error.response?.status === 403) {
      normModal.value?.showPermissionError();
    } else {
      normModal.value?.showError(
        'Ошибка удаления норм',
        error.response?.data?.detail || 'Произошла ошибка при удалении норм'
      );
    }
  }
};;

const fetchNorms = async () => {
  try {
    const response = await axios.get('passenger-car-norms/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    norms.value = response.data;
  } catch (error) {
    console.error('Error fetching norms:', error);
  }
};

const fetchPassengerCars = async () => {
  try {
    const response = await axios.get('passenger-cars/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    passengerCars.value = response.data;
  } catch (error) {
    console.error('Error fetching passenger cars:', error);
  }
};

onMounted(async () => {
  await fetchPassengerCars();
  await fetchNorms();
});
</script>


