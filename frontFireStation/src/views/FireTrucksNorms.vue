<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[95%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Нормы для пожарных автомобилей</h2>
      
      <!-- Filters Section -->
      <div class="bg-white rounded shadow p-6 mb-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <SelectInput
              v-model="filterCar"
              label="Фильтр по автомобилю"
              :options="carsFilterOptions"
              placeholder="Все автомобили"
            />
          </div>
          <div>
            <SelectInput
              v-model="filterSeason"
              label="Фильтр по сезону"
              :options="[
                { value: '', label: 'Все сезоны' },
                { value: 'summer', label: 'Лето' },
                { value: 'winter', label: 'Зима' }
              ]"
              placeholder="Все сезоны"
            />
          </div>
        </div>

        <!-- Table Toggle Controls -->
        <div class="flex gap-4 mt-6 pt-6 border-t">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              v-model="showFuelNormsTable"
              class="w-4 h-4"
            />
            <span :style="{ color: palette.dark }">Нормы расхода топлива пожарных</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              v-model="showOperatingHoursTable"
              class="w-4 h-4"
            />
            <span :style="{ color: palette.dark }">Коэффициенты моточасов</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              v-model="showTechnicalNormsTable"
              class="w-4 h-4"
            />
            <span :style="{ color: palette.dark }">Техническое обслуживание</span>
          </label>
        </div>
      </div>

      <!-- Tables Grid - Adaptive -->
      <div class="grid gap-6" :class="{
        'grid-cols-1': showFuelNormsTable + showOperatingHoursTable + showTechnicalNormsTable === 1,
        'grid-cols-1 lg:grid-cols-2': showFuelNormsTable + showOperatingHoursTable + showTechnicalNormsTable === 2,
        'grid-cols-1 lg:grid-cols-3': showFuelNormsTable + showOperatingHoursTable + showTechnicalNormsTable === 3,
      }">
        <!-- Table 1: Fuel Norms -->
        <div v-if="showFuelNormsTable" class="bg-white rounded shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold" :style="{ color: palette.dark }">
              Нормы расхода топлива пожарных
            </h3>
          </div>
          <div class="flex gap-2 mb-4">
            <Button
              v-if="auth.permissions.can_create_fire_truck_norms"
              variant="primary"
              size="sm"
              @click="openCreateFuelNormModal"
            >
              + Создать норму топлива
            </Button>
            <Button
              v-if="auth.permissions.can_delete_fire_truck_norms"
              variant="danger"
              size="sm"
              @click="openDeleteFuelNormsModal"
              :disabled="selectedFuelNormIds.length === 0"
            >
              {{ deleteFuelNormsLabel }}
            </Button>
          </div>
          <DataTable
            :data="filteredFuelNorms"
            :columns="fuelNormsColumns"
            :selectable="true"
            :show-select-all="false"
            :selected-rows="getSelectedFuelNormIndexes()"
            @row-selected="onFuelNormsSelected"
          >
            <template #cell-car="{ value }">
              {{ getCar(value)?.number }}
            </template>
            <template #cell-km_norm="{ value }">
              {{ parseFloat(value).toFixed(3) }}
            </template>
            <template #cell-with_pump_norm="{ value }">
              {{ parseFloat(value).toFixed(3) }}
            </template>
          </DataTable>
        </div>

        <!-- Table 2: Operating Hours Norms -->
        <div v-if="showOperatingHoursTable" class="bg-white rounded shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold" :style="{ color: palette.dark }">
              Коэффициенты моточасов
            </h3>
          </div>
          <div class="flex gap-2 mb-4">
            <Button
              v-if="auth.permissions.view_operating_hours"
              variant="primary"
              size="sm"
              @click="openCreateOperatingHoursModal"
            >
              + Создать коэффициент
            </Button>
            <Button
              v-if="auth.permissions.view_operating_hours"
              variant="danger"
              size="sm"
              @click="openDeleteOperatingHoursModal"
              :disabled="selectedOperatingHourIds.length === 0"
            >
              {{ deleteOperatingHoursLabel }}
            </Button>
          </div>
          <DataTable
            :data="filteredOperatingHoursNorms"
            :columns="operatingHoursColumns"
            :selectable="true"
            :show-select-all="false"
            :selected-rows="getSelectedOperatingHourIndexes()"
            @row-selected="onOperatingHoursSelected"
          >
            <template #cell-car="{ value }">
              {{ getCar(value)?.number }}
            </template>
            <template #cell-km_norm="{ value }">
              {{ parseFloat(value).toFixed(4) }}
            </template>
            <template #cell-with_pump_norm="{ value }">
              {{ parseFloat(value).toFixed(4) }}
            </template>
          </DataTable>
        </div>

        <!-- Table 3: Technical Maintenance Norms -->
        <div v-if="showTechnicalNormsTable" class="bg-white rounded shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold" :style="{ color: palette.dark }">
              Техническое обслуживание
            </h3>
          </div>
          <div class="flex gap-2 mb-4">
            <Button
              v-if="auth.permissions.can_create_technical_maintenance"
              variant="primary"
              size="sm"
              @click="openCreateTechnicalNormModal"
            >
              + Создать ТО
            </Button>
            <Button
              v-if="auth.permissions.can_delete_technical_maintenance"
              variant="danger"
              size="sm"
              @click="openDeleteTechnicalNormsModal"
              :disabled="selectedTechnicalNormIds.length === 0"
            >
              {{ deleteTechnicalNormsLabel }}
            </Button>
          </div>
          <DataTable
            :data="filteredTechnicalNorms"
            :columns="technicalNormsColumns"
            :selectable="true"
            :show-select-all="false"
            :selected-rows="getSelectedTechnicalNormIndexes()"
            @row-selected="onTechnicalNormsSelected"
          >
            <template #cell-fire_truck="{ value }">
              {{ getCar(value)?.number }}
            </template>
            <template #cell-norm="{ value }">
              {{ parseFloat(value).toFixed(3) }}
            </template>
          </DataTable>
        </div>
      </div>
    </div>
  </div>

  <PermissionDeniedModal ref="permissionDeniedModal" />
  <ErrorModal ref="errorModalRef" />

  <!-- Modal подтверждения удаления нормы топлива -->
  <Modal
    :is-open="showDeleteFuelNormsModal"
    title="Подтвердить удаление норм расхода топлива пожарных"
    @close="closeDeleteFuelNormsModal"
  >
    <div class="space-y-4">
      <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующие нормы расхода топлива пожарных:</p>
      <div class="bg-red-50 border border-red-200 rounded p-4">
        <ul class="space-y-2">
          <li v-for="norm in fuelNormsToDelete" :key="norm.id" :style="{ color: palette.dark }">
            {{ getCar(norm.car)?.number }} - л/км: {{ parseFloat(norm.km_norm).toFixed(3) }}, С насосом: {{ parseFloat(norm.with_pump_norm).toFixed(3) }}
          </li>
        </ul>
      </div>
    </div>
    <template #footer>
      <Button variant="secondary" size="md" @click="closeDeleteFuelNormsModal">Закрыть</Button>
      <Button variant="danger" size="md" @click="confirmDeleteFuelNorms">Удалить</Button>
    </template>
  </Modal>

  <!-- Modal подтверждения удаления коэффициентов моточасов -->
  <Modal
    :is-open="showDeleteOperatingHoursModal"
    title="Подтвердить удаление коэффициентов моточасов"
    @close="closeDeleteOperatingHoursModal"
  >
    <div class="space-y-4">
      <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующие коэффициенты моточасов:</p>
      <div class="bg-red-50 border border-red-200 rounded p-4">
        <ul class="space-y-2">
          <li v-for="norm in operatingHoursToDelete" :key="norm.id" :style="{ color: palette.dark }">
            {{ getCar(norm.car)?.number }} - км: {{ parseFloat(norm.km_norm).toFixed(4) }}, С насосом: {{ parseFloat(norm.with_pump_norm).toFixed(4) }}
          </li>
        </ul>
      </div>
    </div>
    <template #footer>
      <Button variant="secondary" size="md" @click="closeDeleteOperatingHoursModal">Закрыть</Button>
      <Button variant="danger" size="md" @click="confirmDeleteOperatingHours">Удалить</Button>
    </template>
  </Modal>

  <!-- Modal подтверждения удаления ТО -->
  <Modal
    :is-open="showDeleteTechnicalNormsModal"
    title="Подтвердить удаление технического обслуживания"
    @close="closeDeleteTechnicalNormsModal"
  >
    <div class="space-y-4">
      <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующие записи ТО:</p>
      <div class="bg-red-50 border border-red-200 rounded p-4">
        <ul class="space-y-2">
          <li v-for="norm in technicalNormsToDelete" :key="norm.id" :style="{ color: palette.dark }">
            {{ getCar(norm.fire_truck)?.number }} - {{ norm.maintenance_type }}: {{ parseFloat(norm.norm).toFixed(3) }}
          </li>
        </ul>
      </div>
    </div>
    <template #footer>
      <Button variant="secondary" size="md" @click="closeDeleteTechnicalNormsModal">Закрыть</Button>
      <Button variant="danger" size="md" @click="confirmDeleteTechnicalNorms">Удалить</Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { palette, SelectInput, Button, DataTable, Modal } from '../components/ui/importUi';
import NavigationMenu from '../components/NavigationMenu.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import ErrorModal from '../components/ErrorModal.vue';
import axios from 'axios';

const auth = useAuthStore();
const permissionDeniedModal = ref(null);
const errorModalRef = ref(null);

// Modal states
const showDeleteFuelNormsModal = ref(false);
const showDeleteOperatingHoursModal = ref(false);
const showDeleteTechnicalNormsModal = ref(false);

// Data
const fuelNorms = ref([]);
const operatingHoursNorms = ref([]);
const technicalNorms = ref([]);
const fireTrucks = ref([]);

// UI State - Show/Hide Tables
const showFuelNormsTable = ref(true);
const showOperatingHoursTable = ref(true);
const showTechnicalNormsTable = ref(true);

// Selection State - Selected IDs
const selectedFuelNormIds = ref([]);
const selectedOperatingHourIds = ref([]);
const selectedTechnicalNormIds = ref([]);

// Filters
const filterCar = ref('');
const filterSeason = ref('');

// Computed - Filter Options
const carsFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все автомобили' },
    ...fireTrucks.value.map(truck => ({
      value: truck.id,
      label: `${truck.number} - ${truck.brand} ${truck.model}`
    }))
  ];
});

// Computed - Filtered Data
const filteredFuelNorms = computed(() => {
  let filtered = fuelNorms.value;

  if (filterCar.value) {
    filtered = filtered.filter(n => n.car === parseInt(filterCar.value));
  }

  if (filterSeason.value) {
    filtered = filtered.filter(n => n.season === filterSeason.value);
  }

  return filtered;
});

const filteredOperatingHoursNorms = computed(() => {
  let filtered = operatingHoursNorms.value;

  if (filterCar.value) {
    filtered = filtered.filter(n => n.car === parseInt(filterCar.value));
  }

  return filtered;
});

const filteredTechnicalNorms = computed(() => {
  let filtered = technicalNorms.value;

  if (filterCar.value) {
    filtered = filtered.filter(n => n.fire_truck === parseInt(filterCar.value));
  }

  return filtered;
});

// Computed - Delete Button Labels
const deleteFuelNormsLabel = computed(() => {
  const count = selectedFuelNormIds.value.length;
  if (count === 0) return 'Удалить норму';
  if (count === 1) return 'Удалить норму';
  return `Удалить норм (${count})`;
});

const deleteOperatingHoursLabel = computed(() => {
  const count = selectedOperatingHourIds.value.length;
  if (count === 0) return 'Удалить коэффициент';
  if (count === 1) return 'Удалить коэффициент';
  return `Удалить коэффициенты (${count})`;
});

const deleteTechnicalNormsLabel = computed(() => {
  const count = selectedTechnicalNormIds.value.length;
  if (count === 0) return 'Удалить ТО';
  if (count === 1) return 'Удалить ТО';
  return `Удалить ТО (${count})`;
});

// Computed - Items to delete
const fuelNormsToDelete = computed(() => {
  return filteredFuelNorms.value.filter(n => selectedFuelNormIds.value.includes(n.id));
});

const operatingHoursToDelete = computed(() => {
  return filteredOperatingHoursNorms.value.filter(n => selectedOperatingHourIds.value.includes(n.id));
});

const technicalNormsToDelete = computed(() => {
  return filteredTechnicalNorms.value.filter(n => selectedTechnicalNormIds.value.includes(n.id));
});

// Column Definitions for DataTable
const fuelNormsColumns = [
  { key: 'car', label: 'Машина' },
  { key: 'km_norm', label: 'Норма л/км' },
  { key: 'with_pump_norm', label: 'С насосом' }
];

const operatingHoursColumns = [
  { key: 'car', label: 'Машина' },
  { key: 'km_norm', label: 'Норма км' },
  { key: 'with_pump_norm', label: 'С насосом' }
];

const technicalNormsColumns = [
  { key: 'fire_truck', label: 'Машина' },
  { key: 'maintenance_type', label: 'Вид ТО' },
  { key: 'norm', label: 'Норма' }
];

// Methods - Helpers
const getCar = (carId) => {
  return fireTrucks.value.find(t => t.id === carId);
};

// Get selected indexes for DataTable
const getSelectedFuelNormIndexes = () => {
  return filteredFuelNorms.value.map((norm, idx) => 
    selectedFuelNormIds.value.includes(norm.id) ? idx : -1
  ).filter(idx => idx !== -1);
};

const getSelectedOperatingHourIndexes = () => {
  return filteredOperatingHoursNorms.value.map((norm, idx) => 
    selectedOperatingHourIds.value.includes(norm.id) ? idx : -1
  ).filter(idx => idx !== -1);
};

const getSelectedTechnicalNormIndexes = () => {
  return filteredTechnicalNorms.value.map((norm, idx) => 
    selectedTechnicalNormIds.value.includes(norm.id) ? idx : -1
  ).filter(idx => idx !== -1);
};

// Handle row selection from DataTable
const onFuelNormsSelected = (selectedIndexes) => {
  selectedFuelNormIds.value = selectedIndexes.map(idx => filteredFuelNorms.value[idx].id);
};

const onOperatingHoursSelected = (selectedIndexes) => {
  selectedOperatingHourIds.value = selectedIndexes.map(idx => filteredOperatingHoursNorms.value[idx].id);
};

const onTechnicalNormsSelected = (selectedIndexes) => {
  selectedTechnicalNormIds.value = selectedIndexes.map(idx => filteredTechnicalNorms.value[idx].id);
};

// Methods - Fetch Data
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

const fetchFuelNorms = async () => {
  if (!auth.permissions.view_fire_truck_norms) {
    permissionDeniedModal.value?.openModal('view_fire_truck_norms');
    return;
  }
  try {
    const response = await axios.get('fire-truck-norms/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fuelNorms.value = response.data;
    console.log('FireTruck Fuel Norms loaded:', response.data);
  } catch (error) {
    console.error('Error fetching fuel norms:', error);
  }
};

const fetchOperatingHoursNorms = async () => {
  if (!auth.permissions.view_operating_hours) {
    permissionDeniedModal.value?.openModal('view_operating_hours');
    return;
  }
  try {
    const response = await axios.get('fire-truck-operating-hours-norms/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    operatingHoursNorms.value = response.data;
    console.log('FireTruck Operating Hours Norms loaded:', response.data);
  } catch (error) {
    console.error('Error fetching operating hours norms:', error);
  }
};

const fetchTechnicalNorms = async () => {
  if (!auth.permissions.view_technical_maintenance) {
    permissionDeniedModal.value?.openModal('view_technical_maintenance');
    return;
  }
  try {
    const response = await axios.get('technical-maintenance-norms/?fire_truck__isnull=false', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    technicalNorms.value = response.data;
    console.log('Technical Maintenance Norms (Fire Trucks) loaded:', response.data);
  } catch (error) {
    console.error('Error fetching technical norms:', error);
  }
};

// Methods - Delete Norms
const openDeleteFuelNormsModal = () => {
  if (selectedFuelNormIds.value.length === 0) {
    return;
  }
  if (!auth.permissions.can_delete_fire_truck_norms) {
    permissionDeniedModal.value?.openModal('can_delete_fire_truck_norms');
    return;
  }
  showDeleteFuelNormsModal.value = true;
};

const closeDeleteFuelNormsModal = () => {
  showDeleteFuelNormsModal.value = false;
};

const confirmDeleteFuelNorms = async () => {
  try {
    for (const id of selectedFuelNormIds.value) {
      await axios.delete(`/fire-truck-norms/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[FireTrucksNorms] Fuel norms deleted successfully');
    
    fuelNorms.value = fuelNorms.value.filter(n => !selectedFuelNormIds.value.includes(n.id));
    selectedFuelNormIds.value = [];
    closeDeleteFuelNormsModal();
  } catch (error) {
    console.error('Ошибка при удалении нормы:', error);
    errorModalRef.value?.openModal(error);
    closeDeleteFuelNormsModal();
  }
};

const openDeleteOperatingHoursModal = () => {
  if (selectedOperatingHourIds.value.length === 0) {
    return;
  }
  if (!auth.permissions.view_operating_hours) {
    permissionDeniedModal.value?.openModal('view_operating_hours');
    return;
  }
  showDeleteOperatingHoursModal.value = true;
};

const closeDeleteOperatingHoursModal = () => {
  showDeleteOperatingHoursModal.value = false;
};

const confirmDeleteOperatingHours = async () => {
  try {
    for (const id of selectedOperatingHourIds.value) {
      await axios.delete(`/fire-truck-operating-hours-norms/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[FireTrucksNorms] Operating hours norms deleted successfully');
    
    operatingHoursNorms.value = operatingHoursNorms.value.filter(n => !selectedOperatingHourIds.value.includes(n.id));
    selectedOperatingHourIds.value = [];
    closeDeleteOperatingHoursModal();
  } catch (error) {
    console.error('Ошибка при удалении коэффициента:', error);
    errorModalRef.value?.openModal(error);
    closeDeleteOperatingHoursModal();
  }
};

const openDeleteTechnicalNormsModal = () => {
  if (selectedTechnicalNormIds.value.length === 0) {
    return;
  }
  if (!auth.permissions.can_delete_technical_maintenance) {
    permissionDeniedModal.value?.openModal('can_delete_technical_maintenance');
    return;
  }
  showDeleteTechnicalNormsModal.value = true;
};

const closeDeleteTechnicalNormsModal = () => {
  showDeleteTechnicalNormsModal.value = false;
};

const confirmDeleteTechnicalNorms = async () => {
  try {
    for (const id of selectedTechnicalNormIds.value) {
      await axios.delete(`/technical-maintenance-norms/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[FireTrucksNorms] Technical norms deleted successfully');
    
    technicalNorms.value = technicalNorms.value.filter(n => !selectedTechnicalNormIds.value.includes(n.id));
    selectedTechnicalNormIds.value = [];
    closeDeleteTechnicalNormsModal();
  } catch (error) {
    console.error('Ошибка при удалении ТО:', error);
    errorModalRef.value?.openModal(error);
    closeDeleteTechnicalNormsModal();
  }
};

// Placeholder methods for create modals (can be implemented later)
const openCreateFuelNormModal = () => {
  console.log('Create fuel norm modal - to be implemented');
};

const openCreateOperatingHoursModal = () => {
  console.log('Create operating hours modal - to be implemented');
};

const openCreateTechnicalNormModal = () => {
  console.log('Create technical norm modal - to be implemented');
};

onMounted(async () => {
  await Promise.all([
    fetchFireTrucks(),
    fetchFuelNorms(),
    fetchOperatingHoursNorms(),
    fetchTechnicalNorms()
  ]);
});
</script>

<style scoped>
/* DataTable and components use theme.js for styling */
</style>
