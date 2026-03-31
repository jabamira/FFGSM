<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Путевые листы пожарных автомобилей</h2>
      
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <!-- Filters Row 1 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <SelectInput
              v-model="filterCar"
              label="Автомобиль"
              :options="carsFilterOptions"
              placeholder="Все автомобили"
            />
          </div>
          <div v-if="auth.permissions.view_drivers">
            <SelectInput
              v-model="filterDriver"
              label="Водитель"
              :options="driversFilterOptions"
              placeholder="Все водители"
            />
          </div>
          <div>
            <SelectInput
              v-model="filterSeason"
              label="Сезон"
              :options="[
                { value: '', label: 'Все сезоны' },
                { value: 'summer', label: 'Лето' },
                { value: 'winter', label: 'Зима' }
              ]"
              placeholder="Все сезоны"
            />
          </div>
        </div>

        <!-- Filters Row 2 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <TextInput
              v-model="searchQuery"
              label="Поиск"
              type="text"
              placeholder="Введите поисковую фразу..."
            />
          </div>
          <div class="lg:col-span-2">
            <DateRangeInput
              :modelValue="dateRange"
              @update:modelValue="(val) => dateRange = val"
              label="Период"
              startLabel="От"
              endLabel="До"
            />
          </div>
        </div>

        <!-- DataTable -->
        <DataTable
          :columns="columns"
          :data="filteredWaybills"
          :selectedIds="selectedWaybillIds"
          @select="(ids) => selectedWaybillIds = ids"
          :hideActions="false"
        >
          <template #cell-car="{ row }">
            {{ getCar(row.car)?.number || '-' }} ({{ getCar(row.car)?.brand }} {{ getCar(row.car)?.model }})
          </template>
          <template #cell-driver="{ row }">
            {{ getDriver(row.driver) ? `${getDriver(row.driver).name} ${getDriver(row.driver).surname} ${getDriver(row.driver).last_name}`.trim() : '-' }}
          </template>
          <template #cell-date="{ row }">
            {{ formatDate(row.date) }}
          </template>
          <template #cell-norm_season="{ row }">
            {{ row.norm_season === 'summer' ? 'Лето' : 'Зима' }}
          </template>
          <template #actions="{ row }">
            <button
              @click="openEditWaybillModal(row)"
              class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 mr-2"
            >
              Редактировать
            </button>
          </template>
        </DataTable>
      </div>

      <!-- Blank spacer for bottom nav -->
      <div class="pb-16"></div>
      <WaybillEditModal
        ref="waybillModal"
        :carOptions="carOptions"
        :driverOptions="driverOptions"
        @add="handleAddWaybill"
        @edit="handleEditWaybill"
        @delete="handleDeleteWaybills"
      />

      <!-- CRUD Panel -->
      <CrudPanel
        @create="openAddWaybillModal"
        @delete="openDeleteWaybillModal"
        createLabel="Создать путевой лист"
        :deleteLabel="deleteButtonLabel"
        :isDeleteDisabled="isDeleteDisabled"
      />
    </div>
  </div>
  <PermissionDeniedModal ref="permissionDeniedModal" />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { palette, SelectInput, TextInput, DateRangeInput } from '../components/ui/importUi';
import { useSearch } from '../composables/useSearch';
import CrudPanel from '../components/CrudPanel.vue';
import DataTable from '../components/ui/DataTable.vue';
import NavigationMenu from '../components/NavigationMenu.vue';
import WaybillEditModal from '../components/WaybillEditModal.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import axios from 'axios';
import { formatFuelType } from '../config/fuelTypes';

const auth = useAuthStore();
const permissionDeniedModal = ref(null);

// Data
const waybills = ref([]);
const fireTrucks = ref([]);
const drivers = ref([]);

// Selection and Modals
const selectedWaybillIds = ref([]);
const waybillModal = ref(null);

// Filters
const filterCar = ref('');
const filterDriver = ref('');
const filterSeason = ref('');
const dateRange = ref({ start: '', end: '' });

// Prepare waybills for search with searchable text fields
const waybillsForSearch = computed(() => {
  return waybills.value.map(w => {
    const car = getCar(w.car);
    const driver = getDriver(w.driver);
    const carText = car ? `${car.number} ${car.brand} ${car.model}` : '';
    const driverText = driver ? `${driver.name} ${driver.surname} ${driver.last_name}`.trim() : '';
    const seasonText = w.norm_season === 'summer' ? 'лето' : 'зима';
    
    return {
      ...w,
      searchText: `${w.number} ${carText} ${driverText} ${seasonText}`
    };
  });
});

// Search with useSearch composable
const { searchQuery, filtered: searchFiltered } = useSearch(waybillsForSearch, ['searchText']);

// Computed
const carOptions = computed(() => {
  return fireTrucks.value.map(truck => ({
    value: truck.id,
    label: `${truck.number} - ${truck.brand} ${truck.model}`
  }));
});

const driverOptions = computed(() => {
  return drivers.value.map(driver => ({
    value: driver.id,
    label: `${driver.name} ${driver.surname} ${driver.last_name}`.trim()
  }));
});

const carsFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все автомобили' },
    ...fireTrucks.value.map(truck => ({
      value: truck.id,
      label: `${truck.number} - ${truck.brand} ${truck.model}`
    }))
  ];
});

const driversFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все водители' },
    ...drivers.value.map(driver => ({
      value: driver.id,
      label: `${driver.name} ${driver.surname} ${driver.last_name}`.trim()
    }))
  ];
});

const filteredWaybills = computed(() => {
  // Start with search results
  let filtered = searchFiltered.value;

  if (filterCar.value) {
    filtered = filtered.filter(w => w.car === parseInt(filterCar.value));
  }

  if (filterDriver.value) {
    filtered = filtered.filter(w => w.driver === parseInt(filterDriver.value));
  }

  if (filterSeason.value) {
    filtered = filtered.filter(w => w.norm_season === filterSeason.value);
  }

  if (dateRange.value.start) {
    filtered = filtered.filter(w => w.date >= dateRange.value.start);
  }

  if (dateRange.value.end) {
    filtered = filtered.filter(w => w.date <= dateRange.value.end);
  }

  return filtered;
});

const columns = computed(() => [
  { key: 'number', label: 'Номер', sortable: true },
  { key: 'car', label: 'Автомобиль', sortable: false },
  { key: 'driver', label: 'Водитель', sortable: false },
  { key: 'date', label: 'Дата', sortable: true },
  { key: 'norm_season', label: 'Сезон', sortable: true }
]);

// Methods
const getCar = (carId) => {
  return fireTrucks.value.find(t => t.id === carId);
};

const getDriver = (driverId) => {
  return drivers.value.find(d => d.id === driverId);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU');
};

const openAddWaybillModal = () => {
  waybillModal.value?.openAddModal();
};

const openDeleteWaybillModal = () => {
  waybillModal.value?.openDeleteModal(selectedWaybillIds.value.length);
};

const openEditWaybillModal = (waybill) => {
  waybillModal.value?.openEditModal(waybill);
};

const handleAddWaybill = async (waybillData) => {
  try {
    await axios.post('fire-truck-waybills/', waybillData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    await fetchWaybills();
  } catch (error) {
    waybillModal.value?.showError(
      'Ошибка создания путевого листа',
      error.response?.data?.detail || 'Произошла ошибка при создании путевого листа'
    );
  }
};

const handleEditWaybill = async (waybillData) => {
  try {
    await axios.patch(`fire-truck-waybills/${waybillData.id}/`, waybillData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    await fetchWaybills();
  } catch (error) {
    waybillModal.value?.showError(
      'Ошибка обновления путевого листа',
      error.response?.data?.detail || 'Произошла ошибка при обновлении путевого листа'
    );
  }
};

const handleDeleteWaybills = async () => {
  try {
    for (const id of selectedWaybillIds.value) {
      await axios.delete(`fire-truck-waybills/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    await fetchWaybills();
    selectedWaybillIds.value = [];
  } catch (error) {
    if (error.response?.status === 403) {
      waybillModal.value?.showPermissionError();
    } else {
      waybillModal.value?.showError(
        'Ошибка удаления путевого листа',
        error.response?.data?.detail || 'Произошла ошибка при удалении путевого листа'
      );
    }
  }
};

const fetchWaybills = async () => {
  if (!auth.permissions.view_fire_truck_waybills) {
    permissionDeniedModal.value?.openModal('view_fire_truck_waybills');
    return;
  }
  try {
    const response = await axios.get('fire-truck-waybills/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    waybills.value = response.data;
  } catch (error) {
    console.error('Error fetching waybills:', error);
  }
};

const fetchFireTrucks = async () => {
  if (!auth.permissions.view_fire_trucks) {
    permissionDeniedModal.value?.openModal('view_fire_trucks');
    return;
  }
  try {
    const response = await axios.get('fire-trucks/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fireTrucks.value = response.data;
  } catch (error) {
    console.error('Error fetching fire trucks:', error);
  }
};

const fetchDrivers = async () => {
  if (!auth.permissions.view_drivers) {
    permissionDeniedModal.value?.openModal('view_drivers');
    return;
  }
  try {
    const response = await axios.get('users/drivers/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    drivers.value = response.data;
  } catch (error) {
    console.error('Error fetching drivers:', error);
  }
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_fire_truck_waybills || false,
    canDelete: auth.permissions.can_delete_fire_truck_waybills || false,
  });
};

const deleteButtonLabel = computed(() => {
  const count = selectedWaybillIds.value.length;
  if (count === 0) return 'Удалить путевой лист';
  if (count === 1) return 'Удалить путевой лист';
  return `Удалить путевых листов (${count})`;
});

const isDeleteDisabled = computed(() => selectedWaybillIds.value.length === 0);

onMounted(async () => {
  setupCrudPermissions();
  
  const fetchTasks = [];
  
  if (auth.permissions.view_fire_trucks) {
    fetchTasks.push(fetchFireTrucks());
  }
  
  if (auth.permissions.view_drivers) {
    fetchTasks.push(fetchDrivers());
  }
  
  if (fetchTasks.length > 0) {
    await Promise.all(fetchTasks);
  }
  
  await fetchWaybills();
});
</script>
