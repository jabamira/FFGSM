<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-2xl font-semibold" :style="{ color: palette.dark }">Управление путевым листом</h2>
        <Button
          @click="goBack"
          variant="secondary"
          size="md"
        >
          ← Вернуться
        </Button>
      </div>

      <!-- Waybill Info Card -->
      <div class="bg-white rounded shadow p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
          <div class="text-center">
            <p :style="{ color: palette.medium }" class="text-xs uppercase">Номер путевого листа</p>
            <p class="font-semibold text-lg" :style="{ color: palette.dark }">№{{ waybill.number }}</p>
          </div>
          <div class="text-center">
            <p :style="{ color: palette.medium }" class="text-xs uppercase">Автомобиль</p>
            <p class="font-semibold text-lg" :style="{ color: palette.dark }">{{ carInfo?.number }}</p>
          </div>
          <div class="text-center">
            <p :style="{ color: palette.medium }" class="text-xs uppercase">Водитель</p>
            <p class="font-semibold text-lg" :style="{ color: palette.dark }">{{ driverName }}</p>
          </div>
          <div class="text-center">
            <p :style="{ color: palette.medium }" class="text-xs uppercase">Дата</p>
            <p class="font-semibold text-lg" :style="{ color: palette.dark }">{{ formatDate(waybill.date) }}</p>
          </div>
          <div class="text-center">
            <p :style="{ color: palette.medium }" class="text-xs uppercase">Сезон</p>
            <p class="font-semibold text-lg" :style="{ color: palette.dark }">
              {{ waybill.norm_season === 'summer' ? 'Лето' : 'Зима' }}
            </p>
          </div>
        </div>

        <!-- Edit Button -->
        <div class="mt-4 pt-4 border-t" :style="{ borderColor: palette.light }">
          <Button
            @click="openEditModal"
            variant="primary"
            size="md"
          >
            Редактировать путевой лист
          </Button>
        </div>
      </div>

      <!-- Records Table Section -->
      <div class="bg-white rounded shadow p-6">
        <h3 class="text-xl font-semibold mb-4" :style="{ color: palette.dark }">Записи маршрута</h3>

        <!-- Loading state -->
        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2" :style="{ borderColor: palette.dark }"></div>
            <p class="mt-2" :style="{ color: palette.dark }">Загрузка записей...</p>
          </div>
        </div>

        <!-- DataTable -->
        <div v-else class="mb-6">
          <DataTable
            :columns="recordsColumns"
            :data="records"
            :selectedIds="selectedRecordIds"
            @select="(ids) => selectedRecordIds = ids"
            :hideActions="false"
          >
            <template #cell-target="{ value }">
              <span :style="{ color: palette.dark }">{{ value || '-' }}</span>
            </template>
            <template #cell-departure_time="{ value }">
              <span :style="{ color: palette.dark }">{{ value || '-' }}</span>
            </template>
            <template #cell-arrival_time="{ value }">
              <span :style="{ color: palette.dark }">{{ value || '-' }}</span>
            </template>
            <template #cell-distance_city_km="{ value }">
              <span :style="{ color: palette.dark }">{{ value }} км</span>
            </template>
            <template #cell-distance_area_km="{ value }">
              <span :style="{ color: palette.dark }">{{ value }} км</span>
            </template>
            <template #cell-fuel_refueled="{ value }">
              <span :style="{ color: palette.dark }">{{ value ? value + ' л' : '-' }}</span>
            </template>
            <template #cell-fuel_used="{ value }">
              <span :style="{ color: palette.dark }">{{ value }} л</span>
            </template>
            <template #actions="{ row }">
              <button
                @click="openEditRecord(row)"
                class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 mr-2"
              >
                Редактировать
              </button>
            </template>
          </DataTable>

         
        </div>

        <!-- Summary -->
        <div v-if="records.length > 0" class="bg-gray-50 border border-gray-200 rounded p-4">
          <p class="font-semibold mb-3" :style="{ color: palette.dark }">Итого</p>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Км по городу</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalCityKm }} км</p>
            </div>
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Км по области</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalAreaKm }} км</p>
            </div>
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Заправлено</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalFuelRefueled }} л</p>
            </div>
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Израсходовано</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalFuelUsed }} л</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Blank spacer for bottom nav -->
      <div class="pb-16"></div>

      <!-- CRUD Panel -->
      <CrudPanel
        @create="openAddRecord"
        @delete="openDeleteRecordsModal"
        createLabel="Добавить запись"
        :deleteLabel="deleteRecordsLabel"
        :isDeleteDisabled="isDeleteDisabled"
      />
    </div>
  </div>

  <!-- Edit Waybill Modal -->
  <WaybillFieldsEditModal
    ref="waybillEditModal"
    :carOptions="carOptions"
    :driverOptions="driverOptions"
    @edit="handleEditWaybill"
  />

  <!-- Add/Edit Record Modal -->
  <WaybillRecordEditModal
    ref="recordEditModal"
    @add="handleAddRecord"
    @edit="handleEditRecord"
  />

  <!-- Delete Records Modal -->
  <Modal
    :isOpen="showDeleteRecordsModal"
    title="Подтверждение удаления"
    @close="closeDeleteRecordsModal"
  >
    <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующие записи:</p>
    <div class="bg-red-50 border border-red-200 rounded p-4">
      <ul class="space-y-2">
        <li v-for="record in recordsToDelete" :key="record.id" :style="{ color: palette.dark }">
          {{ record.target }} ({{ record.departure_time }} - {{ record.arrival_time }})
        </li>
      </ul>
    </div>
    <template #footer>
      <Button variant="secondary" size="md" @click="closeDeleteRecordsModal">Отмена</Button>
      <Button variant="danger" size="md" @click="confirmDeleteRecords">Удалить</Button>
    </template>
  </Modal>

  <!-- Modals -->
  <PermissionDeniedModal ref="permissionDeniedModal" />
  <NoSelectionModal ref="noSelectionModal" />
  <ErrorModal ref="errorModalRef" />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { palette, SelectInput, TextInput, Modal, Button } from '../components/ui/importUi';
import NavigationMenu from '../components/NavigationMenu.vue';
import CrudPanel from '../components/CrudPanel.vue';
import DataTable from '../components/ui/DataTable.vue';
import WaybillFieldsEditModal from '../components/WaybillFieldsEditModal.vue';
import WaybillRecordEditModal from '../components/WaybillRecordEditModal.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import NoSelectionModal from '../components/NoSelectionModal.vue';
import ErrorModal from '../components/ErrorModal.vue';
import axios from 'axios';

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

// Data
const waybill = ref({});
const records = ref([]);
const cars = ref([]);
const drivers = ref([]);
const loading = ref(false);

// ID from route
const waybillId = computed(() => parseInt(route.params.id));
const carType = computed(() => {
  return route.path.includes('fire-truck') ? 'fire-truck' : 'passenger-car';
});

// Selection and Modals
const selectedRecordIds = ref([]);
const showDeleteRecordsModal = ref(false);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const errorModalRef = ref(null);
const waybillEditModal = ref(null);
const recordEditModal = ref(null);

// Computed properties
const carInfo = computed(() => {
  if (carType.value === 'fire-truck') {
    return cars.value.find(c => c.id === waybill.value.car);
  } else {
    return cars.value.find(c => c.id === waybill.value.car);
  }
});

const driverInfo = computed(() => {
  const found = drivers.value.find(d => d.id === waybill.value.driver);
  console.log('[WaybillManagement] driverInfo computed:', {
    driverId: waybill.value.driver,
    drivers: drivers.value,
    found: found
  });
  return found;
});

const driverName = computed(() => {
  if (!driverInfo.value) {
    console.log('[WaybillManagement] driverInfo is not found, returning "-"');
    return '-';
  }
  const { name, surname, last_name } = driverInfo.value;
  const fullName = `${name} ${surname} ${last_name || ''}`.trim();
  console.log('[WaybillManagement] driverName computed:', fullName, driverInfo.value);
  return fullName;
});

const carOptions = computed(() => {
  return cars.value.map(c => ({
    value: c.id,
    label: `${c.number} (${c.brand} ${c.model})`
  }));
});

const driverOptions = computed(() => {
  return drivers.value.map(d => ({
    value: d.id,
    label: `${d.name} ${d.surname} ${d.last_name || ''}`.trim()
  }));
});

const recordsColumns = [
  { key: 'target', label: 'Цель выезда', sortable: false },
  { key: 'departure_time', label: 'Выезд', sortable: false },
  { key: 'arrival_time', label: 'Прибытие', sortable: false },
  { key: 'distance_city_km', label: 'По городу (км)', sortable: false },
  { key: 'distance_area_km', label: 'По области (км)', sortable: false },
  { key: 'fuel_refueled', label: 'Заправка (л)', sortable: false },
  { key: 'fuel_used', label: 'Израсходовано (л)', sortable: false }
];

const totalCityKm = computed(() => {
  return records.value.reduce((sum, r) => sum + (r.distance_city_km || 0), 0);
});

const totalAreaKm = computed(() => {
  return records.value.reduce((sum, r) => sum + (r.distance_area_km || 0), 0);
});

const totalFuelRefueled = computed(() => {
  return records.value.reduce((sum, r) => sum + (r.fuel_refueled || 0), 0).toFixed(3);
});

const totalFuelUsed = computed(() => {
  return records.value.reduce((sum, r) => sum + (r.fuel_used || 0), 0).toFixed(3);
});

const recordsToDelete = computed(() => {
  return records.value.filter(r => selectedRecordIds.value.includes(r.id));
});

const deleteRecordsLabel = computed(() => {
  const count = selectedRecordIds.value.length;
  if (count === 0) return 'Удалить запись';
  if (count === 1) return 'Удалить запись';
  return `Удалить записей (${count})`;
});

const isDeleteDisabled = computed(() => selectedRecordIds.value.length === 0);

const canCreateRecords = computed(() => {
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_create_fire_truck_records'
    : 'can_create_passenger_car_records';
  return auth.permissions[permissionKey] || false;
});

const canDeleteRecords = computed(() => {
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_delete_fire_truck_records'
    : 'can_delete_passenger_car_records';
  return auth.permissions[permissionKey] || false;
});

// Methods
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU');
};

const getEndpoint = () => {
  return carType.value === 'fire-truck'
    ? `fire-truck-waybills/${waybillId.value}/`
    : `passenger-car-waybills/${waybillId.value}/`;
};

const getRecordsEndpoint = () => {
  const filterParam = carType.value === 'fire-truck' 
    ? `fire_truck_waybill=${waybillId.value}`
    : `passenger_car_waybill=${waybillId.value}`;
  
  const resource = carType.value === 'fire-truck'
    ? 'fire-truck-records/'
    : 'passenger-car-records/';
    
  return `${resource}?${filterParam}`;
};

const getCarListEndpoint = () => {
  return carType.value === 'fire-truck' ? 'fire-trucks/?include_odometer=false' : 'passenger-cars/?include_odometer=false';
};

const fetchWaybill = async () => {
  if (!auth.permissions.view_fire_truck_waybills && !auth.permissions.view_passenger_cars_waybills) {
    permissionDeniedModal.value?.openModal('view waybills');
    return;
  }
  try {
    const response = await axios.get(getEndpoint(), {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    waybill.value = response.data;
    console.log('[WaybillManagement] Waybill loaded:', waybill.value);
    console.log('[WaybillManagement] Waybill driver ID:', waybill.value.driver);
  } catch (error) {
    console.error('Error loading waybill:', error);
    errorModalRef.value?.openModal(error);
  }
};

const fetchRecords = async () => {
  loading.value = true;
  try {
    const response = await axios.get(getRecordsEndpoint(), {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    records.value = response.data;
  } catch (error) {
    console.error('Error loading records:', error);
    records.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchCars = async () => {
  try {
    const response = await axios.get(getCarListEndpoint(), {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    cars.value = response.data;
  } catch (error) {
    console.error('Error loading cars:', error);
  }
};

const fetchDrivers = async () => {
  try {
    const response = await axios.get('users/drivers/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    drivers.value = response.data;
    console.log('[WaybillManagement] Drivers loaded:', drivers.value);
  } catch (error) {
    console.error('Error loading drivers:', error);
  }
};

const openEditModal = () => {
  waybillEditModal.value?.openEditModal(waybill.value);
};

const handleEditWaybill = async (waybillData) => {
  try {
    await axios.patch(getEndpoint(), waybillData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    console.log('[WaybillManagement] Waybill updated successfully');
    await fetchWaybill();
  } catch (error) {
    console.error('Error updating waybill:', error);
    errorModalRef.value?.openModal(error);
  }
};

const openAddRecord = () => {
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_create_fire_truck_records'
    : 'can_create_passenger_car_records';
  
  if (!auth.permissions[permissionKey]) {
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }
  recordEditModal.value?.openAddModal();
};

const openEditRecord = (record) => {
  recordEditModal.value?.openEditModal(record);
};

const handleAddRecord = async (recordData) => {
  try {
    const endpoint = carType.value === 'fire-truck'
      ? 'fire-truck-records/'
      : 'passenger-car-records/';
    
    const payload = {
      ...recordData,
      [carType.value === 'fire-truck' ? 'fire_truck_waybill' : 'passenger_car_waybill']: waybillId.value
    };
    
    await axios.post(endpoint, payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[WaybillManagement] Record added successfully');
    await fetchRecords();
  } catch (error) {
    console.error('Error adding record:', error);
    errorModalRef.value?.openModal(error);
  }
};

const handleEditRecord = async (recordData) => {
  try {
    const endpoint = carType.value === 'fire-truck'
      ? `fire-truck-records/${recordData.id}/`
      : `passenger-car-records/${recordData.id}/`;
    
    await axios.patch(endpoint, recordData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[WaybillManagement] Record updated successfully');
    await fetchRecords();
  } catch (error) {
    console.error('Error updating record:', error);
    errorModalRef.value?.openModal(error);
  }
};

const openDeleteRecordsModal = () => {
  if (selectedRecordIds.value.length === 0) {
    noSelectionModal.value?.openModal();
    return;
  }
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_delete_fire_truck_records'
    : 'can_delete_passenger_car_records';
  
  if (!auth.permissions[permissionKey]) {
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }
  showDeleteRecordsModal.value = true;
};

const closeDeleteRecordsModal = () => {
  showDeleteRecordsModal.value = false;
};

const confirmDeleteRecords = async () => {
  try {
    for (const id of selectedRecordIds.value) {
      const endpoint = carType.value === 'fire-truck'
        ? `fire-truck-records/${id}/`
        : `passenger-car-records/${id}/`;
      
      await axios.delete(endpoint, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[WaybillManagement] Records deleted successfully');
    selectedRecordIds.value = [];
    await fetchRecords();
    closeDeleteRecordsModal();
  } catch (error) {
    console.error('Error deleting records:', error);
    errorModalRef.value?.openModal(error);
    closeDeleteRecordsModal();
  }
};

const goBack = () => {
  router.back();
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: carType.value === 'fire-truck'
      ? auth.permissions.can_create_fire_truck_waybills_record || false
      : auth.permissions.can_create_passenger_cars_waybills_record || false,
    canDelete: carType.value === 'fire-truck'
      ? auth.permissions.can_delete_fire_truck_waybills_record || false
      : auth.permissions.can_delete_passenger_cars_waybills_record || false
  });
};

// Lifecycle
onMounted(async () => {
  const fetchTasks = [fetchWaybill(), fetchRecords(), fetchCars(), fetchDrivers()];
  
  await Promise.all(fetchTasks);
  setupCrudPermissions();
});

onUnmounted(() => {
  auth.clearCrudPermissions();
});
</script>
