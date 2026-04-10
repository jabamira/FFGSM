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
            <p 
              class="font-semibold text-lg cursor-pointer hover:opacity-70 transition-opacity" 
              style="color: #2563EB"
              @click="carType === 'fire-truck' ? openEditFireTruck() : openEditPassengerCar()"
            >
              {{ carInfo?.number }}
            </p>
          </div>
          <div class="text-center">
            <p :style="{ color: palette.medium }" class="text-xs uppercase">Водитель</p>
            <p 
              class="font-semibold text-lg cursor-pointer hover:opacity-70 transition-opacity" 
              style="color: #2563EB"
              @click="openEditDriver()"
            >
              {{ driverName }}
            </p>
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

        <!-- Edit and Delete Buttons -->
        <div class="mt-4 pt-4 border-t" :style="{ borderColor: palette.light }">
          <div class="flex gap-3">
            <Button
              @click="openEditModal"
              variant="primary"
              size="md"
            >
              Редактировать путевой лист
            </Button>
            <Button
              @click="openDeleteWaybillModal"
              variant="danger"
              size="md"
            >
              Удалить путевой лист
            </Button>
          </div>
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
            @row-click="(row) => openEditRecord(row)"
            :hideActions="false"
          >
            <template #cell-target="{ value }">
              <span :style="{ color: palette.dark }">{{ value || '-' }}</span>
            </template>
            <template #cell-departure_time="{ value }">
              <span :style="{ color: palette.dark }">{{ formatTime(value) }}</span>
            </template>
            <template #cell-arrival_time="{ value }">
              <span :style="{ color: palette.dark }">{{ formatTime(value) }}</span>
            </template>
            <template #cell-driving_route="{ value }">
              <span :style="{ color: palette.dark }">{{ value || '-' }}</span>
            </template>
            <template #cell-distance_km="{ value }">
              <span :style="{ color: palette.dark }">{{ formatKilometers(value) }} км</span>
            </template>
            <template #cell-distance_city_km="{ value }">
              <span :style="{ color: palette.dark }">{{ formatKilometers(value) }} км</span>
            </template>
            <template #cell-distance_area_km="{ value }">
              <span :style="{ color: palette.dark }">{{ formatKilometers(value) }} км</span>
            </template>
            <template #cell-time_with_pump="{ value }">
              <span :style="{ color: palette.dark }">{{ value }} мин</span>
            </template>
            <template #cell-fuel_refueled="{ value }">
              <span :style="{ color: palette.dark }">{{ value ? value + ' л' : '-' }}</span>
            </template>
            <template #cell-fuel_used="{ value }">
              <span :style="{ color: palette.dark }">{{ value }} л</span>
            </template>
          </DataTable>

         
        </div>

        <!-- Summary -->
        <div v-if="records.length > 0" class="bg-gray-50 border border-gray-200 rounded p-4">
          <p class="font-semibold mb-3" :style="{ color: palette.dark }">Итого</p>
          <!-- For Passenger Cars -->
          <div v-if="carType === 'passenger-car'" class="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Км по городу</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalCityKm }} км</p>
            </div>
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Км по области</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalAreaKm }} км</p>
            </div>
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Время в пути</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalTravelTime }}</p>
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
          <!-- For Fire Trucks -->
          <div v-else class="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Километры</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalDistance }} км</p>
            </div>
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Работа с насосом (мин)</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalTimeWithPump }} мин</p>
            </div>
            <div>
              <p :style="{ color: palette.medium }" class="text-xs">Продолжительность</p>
              <p class="font-semibold" :style="{ color: palette.dark }">{{ totalTravelTime }}</p>
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
    :is-fire-truck="carType === 'fire-truck'"
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

  <!-- Delete Waybill Modal -->
  <Modal
    :isOpen="showDeleteWaybillModal"
    title="Подтверждение удаления"
    @close="closeDeleteWaybillModal"
  >
    <p :style="{ color: palette.dark }">Вы уверены что хотите удалить путевой лист №{{ waybill.number }}?</p>
    <div class="bg-red-50 border border-red-200 rounded p-4 mt-4">
      <p :style="{ color: palette.dark }">
        Это действие удалит путевой лист и все его записи. Отменить это действие невозможно.
      </p>
    </div>
    <template #footer>
      <Button variant="secondary" size="md" @click="closeDeleteWaybillModal">Отмена</Button>
      <Button variant="danger" size="md" @click="confirmDeleteWaybill">Удалить</Button>
    </template>
  </Modal>

  <!-- Modals -->
  <PermissionDeniedModal ref="permissionDeniedModal" />
  <NoSelectionModal ref="noSelectionModal" />
  <ErrorModal ref="errorModalRef" />

  <!-- Fire Truck Edit Modal -->
  <FireTruckEditModal
    ref="firetruckEditModalRef"
    :is-open="showEditFireTruckModal"
    :truck="editingFireTruck"
    :original-truck="originalFireTruck"
    :can-view-fire-trucks="auth.permissions.view_fire_trucks"
    :has-odometer="editingFireTruck ? hasOdometer(editingFireTruck.id) : false"
    @close="closeEditFireTruckModal"
    @save="handleFireTruckEditSave"
    @odometer-click="openOdometerFromEdit"
  />

  <!-- Passenger Car Edit Modal -->
  <PassengerCarEditModal
    ref="passengerCarEditModalRef"
    :is-open="showEditPassengerCarModal"
    :car="editingPassengerCar"
    :original-car="originalPassengerCar"
    :can-view-passenger-cars="auth.permissions.view_passenger_cars"
    :has-odometer="editingPassengerCar ? hasOdometer(editingPassengerCar.id) : false"
    @close="closeEditPassengerCarModal"
    @save="handlePassengerCarEditSave"
    @odometer-click="openOdometerFromEdit"
  />

  <!-- Odometer Modal -->
  <OdometerModal
    :is-open="showOdometerModal"
    :car-id="odometerData.car"
    :car-type="carType === 'fire-truck' ? 'fire-truck' : 'passenger-car'"
    :is-required="isOdometerRequired"
    :title="carType === 'fire-truck' ? 'Внесение стартовых данных о пожарной машине' : 'Внесение стартовых данных о легковом автомобиле'"
    @close="closeOdometerModal"
    @submitted="handleOdometerSubmitted"
    @skipped="closeOdometerModal"
  />

  <!-- Driver Edit Modal -->
  <UserEditModal
    ref="driverEditModalRef"
    @user-updated="handleDriverUpdated"
  />

  <!-- Fire Truck Norm Modal -->
  <FireTruckNormModal
    ref="firetruckNormModalRef"
    :is-open="showFireTruckNormModal"
    :car-id="normData.carId"
    :car-number="normData.carNumber"
    :season="normData.season"
    @close="showFireTruckNormModal = false"
    @success="handleNormAddSuccess"
  />
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
import FireTruckEditModal from '../components/FireTruckEditModal.vue';
import PassengerCarEditModal from '../components/PassengerCarEditModal.vue';
import OdometerModal from '../components/OdometerModal.vue';
import UserEditModal from '../components/UserEditModal.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import NoSelectionModal from '../components/NoSelectionModal.vue';
import ErrorModal from '../components/ErrorModal.vue';
import FireTruckNormModal from '../components/FireTruckNormModal.vue';
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
const showDeleteWaybillModal = ref(false);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const errorModalRef = ref(null);
const waybillEditModal = ref(null);
const recordEditModal = ref(null);
const firetruckEditModalRef = ref(null);
const passengerCarEditModalRef = ref(null);
const odometerModalRef = ref(null);

// Fire Truck Edit
const showEditFireTruckModal = ref(false);
const editingFireTruck = ref(null);
const originalFireTruck = ref(null);

// Passenger Car Edit
const showEditPassengerCarModal = ref(false);
const editingPassengerCar = ref(null);
const originalPassengerCar = ref(null);

// Driver Edit
const showEditDriverModal = ref(false);
const driverEditModalRef = ref(null);

// Odometer Modal
const showOdometerModal = ref(false);
const isOdometerRequired = ref(false);
const odometerData = ref({
  car: null,
  odometer: '',
  fuel: '',
  date: new Date().toISOString().split('T')[0]
});

// Fire Truck Norm Modal
const showFireTruckNormModal = ref(false);
const firetruckNormModalRef = ref(null);
const pendingRecordData = ref(null);
const normData = ref({
  carId: null,
  carNumber: '',
  season: ''
});

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

const recordsColumns = computed(() => {
  if (carType.value === 'fire-truck') {
    // Columns for fire truck records
    return [
      { key: 'target', label: 'Цель выезда', sortable: false },
      { key: 'departure_time', label: 'Выезд', sortable: false },
      { key: 'arrival_time', label: 'Прибытие', sortable: false },
      { key: 'driving_route', label: 'Маршрут движения', sortable: false },
      { key: 'distance_km', label: 'Пробег (км)', sortable: false },
      { key: 'time_with_pump', label: 'Насос (мин)', sortable: false },
      { key: 'fuel_refueled', label: 'Заправка (л)', sortable: false },
      { key: 'fuel_used', label: 'Израсходовано (л)', sortable: false }
    ];
  } else {
    // Columns for passenger car records
    return [
      { key: 'target', label: 'Цель выезда', sortable: false },
      { key: 'departure_time', label: 'Выезд', sortable: false },
      { key: 'arrival_time', label: 'Прибытие', sortable: false },
      { key: 'distance_city_km', label: 'По городу (км)', sortable: false },
      { key: 'distance_area_km', label: 'По области (км)', sortable: false },
      { key: 'fuel_refueled', label: 'Заправка (л)', sortable: false },
      { key: 'fuel_used', label: 'Израсходовано (л)', sortable: false }
    ];
  }
});

const totalCityKm = computed(() => {
  if (carType.value === 'fire-truck') return 0;
  return records.value.reduce((sum, r) => sum + (r.distance_city_km || 0), 0);
});

const totalAreaKm = computed(() => {
  if (carType.value === 'fire-truck') return 0;
  return records.value.reduce((sum, r) => sum + (r.distance_area_km || 0), 0);
});

const totalDistance = computed(() => {
  if (carType.value !== 'fire-truck') return 0;
  return records.value.reduce((sum, r) => sum + (r.distance_km || 0), 0);
});

const totalTimeWithPump = computed(() => {
  if (carType.value !== 'fire-truck') return 0;
  return records.value.reduce((sum, r) => sum + (r.time_with_pump || 0), 0);
});

const totalFuelRefueled = computed(() => {
  const total = records.value.reduce((sum, r) => sum + (parseFloat(r.fuel_refueled) || 0), 0);
  return parseFloat(total).toFixed(3);
});

const totalFuelUsed = computed(() => {
  const total = records.value.reduce((sum, r) => sum + (parseFloat(r.fuel_used) || 0), 0);
  return parseFloat(total).toFixed(3);
});

// Вспомогательная функция для конвертации времени HH:MM в минуты
const timeToMinutes = (timeStr) => {
  if (!timeStr || typeof timeStr !== 'string') return 0;
  const parts = timeStr.split(':');
  if (parts.length < 2) return 0;
  const hours = parseInt(parts[0]) || 0;
  const minutes = parseInt(parts[1]) || 0;
  return hours * 60 + minutes;
};

// Вспомогательная функция для конвертации минут в HH:MM или только минуты
const minutesToTimeFormat = (totalMinutes) => {
  if (totalMinutes < 60) {
    return `${totalMinutes} мин`;
  }
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (minutes === 0) {
    return `${hours} ч`;
  }
  return `${hours} ч ${minutes} мин`;
};

const totalTravelTime = computed(() => {
  let totalMinutes = 0;
  
  records.value.forEach(record => {
    const departureMinutes = timeToMinutes(record.departure_time);
    const arrivalMinutes = timeToMinutes(record.arrival_time);
    
    let duration = arrivalMinutes - departureMinutes;
    
    // Если время прибытия раньше времени убытия, это означает пересечение дня
    // (например, выезд в 23:00, приезд в 01:00)
    if (duration < 0) {
      duration += 24 * 60; // Добавляем 24 часа в минутах
    }
    
    totalMinutes += duration;
  });
  
  return minutesToTimeFormat(totalMinutes);
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

const canViewRecords = computed(() => {
  const permissionKey = carType.value === 'fire-truck'
    ? 'view_fire_truck_waybills_records'
    : 'view_passenger_cars_waybills_records';
  return auth.permissions[permissionKey] || false;
});

const canCreateRecords = computed(() => {
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_create_fire_truck_waybills_records'
    : 'can_create_passenger_cars_waybills_records';
  return auth.permissions[permissionKey] || false;
});



const canDeleteRecords = computed(() => {
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_delete_fire_truck_waybills_records'
    : 'can_delete_passenger_cars_waybills_records';
  return auth.permissions[permissionKey] || false;
});

// Methods
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU');
};

const formatTime = (timeString) => {
  if (!timeString) return '-';
  // Обрезать секунды если они есть (HH:MM:SS -> HH:MM)
  return timeString.split(':').slice(0, 2).join(':');
};

const formatKilometers = (value) => {
  // Показывать даже 0
  return value ?? 0;
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
  return carType.value === 'fire-truck' ? 'fire-trucks/?include_odometer=true' : 'passenger-cars/?include_odometer=true';
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
    console.log('[WaybillManagement] Records fetched from server:', {
      endpoint: getRecordsEndpoint(),
      totalCount: response.data?.length || 0,
      data: response.data,
      firstRecord: response.data?.[0] || null
    });
  } catch (error) {
    console.error('Error loading records:', error);
    records.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchCars = async () => {
  // Check permissions before fetching
  const viewPermission = carType.value === 'fire-truck' ? 'view_fire_trucks' : 'view_passenger_cars';
  if (!auth.permissions[viewPermission]) {
    console.warn(`No permission to view ${carType.value === 'fire-truck' ? 'fire trucks' : 'passenger cars'}`);
    return;
  }
  
  try {
    const response = await axios.get(getCarListEndpoint(), {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    cars.value = response.data;
    console.log(`[WaybillManagement] Cars loaded (type: ${carType.value}):`, cars.value);
    // Log odometer data
    cars.value.forEach(car => {
      if (car.odometer_fuel_records && car.odometer_fuel_records.length > 0) {
        console.log(`[WaybillManagement] Car ${car.number} has ${car.odometer_fuel_records.length} odometer record(s)`);
      }
    });
  } catch (error) {
    console.error('Error loading cars:', error);
  }
};

const fetchDrivers = async () => {
  // Check permissions before fetching
  if (!auth.permissions.view_drivers && !auth.permissions.view_users) {
    console.warn('No permission to view drivers or users');
    return;
  }
  
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
  // Check permissions before opening edit modal
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_update_fire_truck_waybills'
    : 'can_update_passenger_cars_waybills';
  
  if (!auth.permissions[permissionKey]) {
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }
  
  waybillEditModal.value?.openEditModal(waybill.value);
};

const handleEditWaybill = async (waybillData) => {
  // Check permissions before editing
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_update_fire_truck_waybills'
    : 'can_update_passenger_cars_waybills';
  
  if (!auth.permissions[permissionKey]) {
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }

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

// Fire Truck Edit Methods
const openEditFireTruck = () => {
  if (!auth.permissions.can_update_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_update_fire_trucks');
    return;
  }
  
  if (!carInfo.value) return;
  
  console.log('[WaybillManagement] Opening fire truck edit modal:', carInfo.value);
  if (carInfo.value.odometer_fuel_records) {
    console.log('[WaybillManagement] Loaded odometer records:', carInfo.value.odometer_fuel_records);
  }
  
  originalFireTruck.value = { ...carInfo.value };
  editingFireTruck.value = { ...carInfo.value };
  showEditFireTruckModal.value = true;
};

const closeEditFireTruckModal = () => {
  showEditFireTruckModal.value = false;
  editingFireTruck.value = null;
  originalFireTruck.value = null;
};

const handleFireTruckEditSave = async () => {
  if (firetruckEditModalRef.value) {
    editingFireTruck.value = firetruckEditModalRef.value.getTruck();
  }
  
  await updateFireTruck();
};

const updateFireTruck = async () => {
  if (!auth.permissions.can_update_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_update_fire_trucks');
    return;
  }
  
  if (!editingFireTruck.value) return;
  
  try {
    await axios.patch(`fire-trucks/${editingFireTruck.value.id}/`, editingFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[WaybillManagement] Fire truck updated successfully');
    await fetchCars();
    closeEditFireTruckModal();
  } catch (error) {
    console.error('Error updating fire truck:', error);
    errorModalRef.value?.openModal(error);
  }
};

// Passenger Car Edit Methods
const openEditPassengerCar = () => {
  if (!auth.permissions.can_update_passenger_cars) {
    permissionDeniedModal.value?.openModal('can_update_passenger_cars');
    return;
  }
  
  if (!carInfo.value) return;
  
  console.log('[WaybillManagement] Opening passenger car edit modal:', carInfo.value);
  if (carInfo.value.odometer_fuel_records) {
    console.log('[WaybillManagement] Loaded odometer records:', carInfo.value.odometer_fuel_records);
  }
  
  originalPassengerCar.value = { ...carInfo.value };
  editingPassengerCar.value = { ...carInfo.value };
  showEditPassengerCarModal.value = true;
};

const closeEditPassengerCarModal = () => {
  showEditPassengerCarModal.value = false;
  editingPassengerCar.value = null;
  originalPassengerCar.value = null;
};

const handlePassengerCarEditSave = async () => {
  if (passengerCarEditModalRef.value) {
    editingPassengerCar.value = passengerCarEditModalRef.value.getCar();
  }
  
  await updatePassengerCar();
};

const updatePassengerCar = async () => {
  if (!auth.permissions.can_update_passenger_cars) {
    permissionDeniedModal.value?.openModal('can_update_passenger_cars');
    return;
  }
  
  if (!editingPassengerCar.value) return;
  
  try {
    await axios.patch(`passenger-cars/${editingPassengerCar.value.id}/`, editingPassengerCar.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[WaybillManagement] Passenger car updated successfully');
    await fetchCars();
    closeEditPassengerCarModal();
  } catch (error) {
    console.error('Error updating passenger car:', error);
    errorModalRef.value?.openModal(error);
  }
};

// Driver Edit Methods
const openEditDriver = () => {
  // Check permissions - need to be able to view drivers/users and update users
  if ((!auth.permissions.view_drivers && !auth.permissions.view_users) || !auth.permissions.can_update_users) {
    permissionDeniedModal.value?.openModal('can_update_users');
    return;
  }
  
  if (!driverInfo.value) return;
  
  console.log('[WaybillManagement] Opening driver edit modal:', driverInfo.value);
  driverEditModalRef.value?.openModal(driverInfo.value);
};

const handleDriverUpdated = async () => {
  console.log('[WaybillManagement] Driver updated successfully');
  await fetchDrivers();
};

const openAddRecord = () => {
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_create_fire_truck_waybills_records'
    : 'can_create_passenger_cars_waybills_records';
  
  if (!auth.permissions[permissionKey]) {
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }
  recordEditModal.value?.openAddModal();
};

const openEditRecord = (record) => {
  console.log('[WaybillManagement] openEditRecord called with:', record);
  
  // Check permissions before editing
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_update_fire_truck_waybills_records'
    : 'can_update_passenger_cars_waybills_records';
  
  if (!auth.permissions[permissionKey]) {
    console.warn('[WaybillManagement] Permission denied for:', permissionKey);
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }
  
  if (!recordEditModal.value) {
    console.error('[WaybillManagement] recordEditModal.value is null or undefined!');
    return;
  }
  
  console.log('[WaybillManagement] Opening edit modal with record:', record);
  recordEditModal.value.openEditModal(record);
};

// Форматировать decimal число: заменить запятую на точку и округлить до 3 знаков
const formatDecimalForSubmit = (value) => {
  if (value === null || value === '' || isNaN(value)) return 0;
  // Заменить запятую на точку
  const normalized = String(value).replace(',', '.');
  const num = parseFloat(normalized);
  // Округлить до 3 знаков после запятой
  return parseFloat(num.toFixed(3));
};

const handleAddRecord = async (recordData) => {
  // Check permissions before adding
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_create_fire_truck_waybills_records'
    : 'can_create_passenger_cars_waybills_records';
  
  if (!auth.permissions[permissionKey]) {
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }

  try {
    const endpoint = carType.value === 'fire-truck'
      ? 'fire-truck-records/'
      : 'passenger-car-records/';
    
    // Форматировать decimal поля перед отправкой
    const fuel_refueled = formatDecimalForSubmit(recordData.fuel_refueled);
    const fuel_used = formatDecimalForSubmit(recordData.fuel_used);
    
    const payload = {
      ...recordData,
      fuel_refueled: fuel_refueled,
      fuel_used: fuel_used,
      [carType.value === 'fire-truck' ? 'fire_truck_waybill' : 'passenger_car_waybill']: waybillId.value
    };
    
    console.log('\n========== ОТПРАВЛЯЮ НОВУЮ ЗАПИСЬ ==========');
    console.log('Endpoint:', endpoint);
    console.log('Полный payload:');
    console.log(JSON.stringify(payload, null, 2));
    console.log('==========================================\n');
    
    await axios.post(endpoint, payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[WaybillManagement] Record added successfully');
    await fetchRecords();
    recordEditModal.value?.closeModal();
  } catch (error) {
    const errorData = error.response?.data;
    
    // Распарсим ошибку независимо от формата
    let errorMsg = '';
    if (Array.isArray(errorData) && errorData.length > 0) {
      // Если это массив, возьмём первый элемент
      const firstError = errorData[0];
      if (typeof firstError === 'string') {
        errorMsg = firstError;
      } else if (firstError.non_field_errors && Array.isArray(firstError.non_field_errors)) {
        errorMsg = firstError.non_field_errors[0] || '';
      } else if (typeof firstError === 'object') {
        errorMsg = JSON.stringify(firstError);
      }
    } else if (typeof errorData === 'string') {
      errorMsg = errorData;
    } else if (errorData && errorData.non_field_errors) {
      errorMsg = Array.isArray(errorData.non_field_errors) 
        ? errorData.non_field_errors[0] 
        : errorData.non_field_errors;
    }
    
    console.log('[DEBUG] errorMsg preview:', errorMsg.substring(0, 200));
    
    // Проверка на ошибку валидации одометра
    if (errorMsg.includes('одометр') && errorMsg.includes('не может быть меньше')) {
      recordEditModal.value?.setValidationError(errorMsg);
      return;
    }
    
    // Check if this is a missing norm error for fire truck
    if (carType.value === 'fire-truck' && error.response?.data?.non_field_errors) {
      const normErrorMsg = error.response.data.non_field_errors[0];
      if (normErrorMsg && typeof normErrorMsg === 'string' && normErrorMsg.includes('Не найдена норма')) {
        const match = normErrorMsg.match(/Не найдена норма для (.+?), сезон=(.+?)$/);
        if (match) {
          const carNumber = match[1];
          const seasonDisplay = match[2];
          const season = seasonDisplay === 'Лето' ? 'summer' : 'winter';
          
          pendingRecordData.value = recordData;
          normData.value = {
            carId: waybill.value.car,
            carNumber: carNumber,
            season: season
          };
          showFireTruckNormModal.value = true;
          return;
        }
      }
    }
    
    // Для всех остальных ошибок - показать в модали с автоскроллом
    const errorText = errorMsg || 'Произошла ошибка при сохранении записи';
    recordEditModal.value?.setValidationError(errorText);
  }
};

const handleEditRecord = async (recordData) => {
  // Check permissions before editing
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_update_fire_truck_waybills_records'
    : 'can_update_passenger_cars_waybills_records';
  
  if (!auth.permissions[permissionKey]) {
    permissionDeniedModal.value?.openModal(permissionKey);
    return;
  }

  try {
    // Форматировать decimal поля перед отправкой
    const fuel_refueled = formatDecimalForSubmit(recordData.fuel_refueled);
    const fuel_used = formatDecimalForSubmit(recordData.fuel_used);
    
    const endpoint = carType.value === 'fire-truck'
      ? `fire-truck-records/${recordData.id}/`
      : `passenger-car-records/${recordData.id}/`;
    
    const payload = {
      ...recordData,
      fuel_refueled: fuel_refueled,
      fuel_used: fuel_used
    };
    
    console.log('\n========== РЕДАКТИРУЮ ЗАПИСЬ ==========');
    console.log('Endpoint:', endpoint);
    console.log('ID:', recordData.id);
    console.log('Полный payload:');
    console.log(JSON.stringify(payload, null, 2));
    console.log('======================================\n');
    
    await axios.patch(endpoint, payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[WaybillManagement] Record updated successfully');
    await fetchRecords();
    recordEditModal.value?.closeModal();
  } catch (error) {
    const errorData = error.response?.data;
    
    // Распарсим ошибку независимо от формата
    let errorMsg = '';
    if (Array.isArray(errorData) && errorData.length > 0) {
      // Если это массив, возьмём первый элемент
      const firstError = errorData[0];
      if (typeof firstError === 'string') {
        errorMsg = firstError;
      } else if (firstError.non_field_errors && Array.isArray(firstError.non_field_errors)) {
        errorMsg = firstError.non_field_errors[0] || '';
      } else if (typeof firstError === 'object') {
        errorMsg = JSON.stringify(firstError);
      }
    } else if (typeof errorData === 'string') {
      errorMsg = errorData;
    } else if (errorData && errorData.non_field_errors) {
      errorMsg = Array.isArray(errorData.non_field_errors) 
        ? errorData.non_field_errors[0] 
        : errorData.non_field_errors;
    }
    
    console.error('Error updating record:', error);
    
    // DEBUG: Выведем тип и содержание errorData
    console.log('[DEBUG] errorData type:', typeof errorData);
    console.log('[DEBUG] isArray:', Array.isArray(errorData));
    console.log('[DEBUG] errorMsg includes "одометр":', errorMsg.includes('одометр'));
    console.log('[DEBUG] errorMsg preview:', errorMsg.substring(0, 200));
    
    // Проверка на ошибку валидации одометра
    if (errorMsg.includes('одометр') && errorMsg.includes('не может быть меньше')) {
      recordEditModal.value?.setValidationError(errorMsg);
      return;
    }
    
    // Check if this is a missing norm error for fire truck
    if (carType.value === 'fire-truck' && error.response?.data?.non_field_errors) {
      const normErrorMsg = error.response.data.non_field_errors[0];
      if (normErrorMsg && typeof normErrorMsg === 'string' && normErrorMsg.includes('Не найдена норма')) {
        const match = normErrorMsg.match(/Не найдена норма для (.+?), сезон=(.+?)$/);
        if (match) {
          const carNumber = match[1];
          const seasonDisplay = match[2];
          const season = seasonDisplay === 'Лето' ? 'summer' : 'winter';
          
          pendingRecordData.value = recordData;
          normData.value = {
            carId: waybill.value.car,
            carNumber: carNumber,
            season: season
          };
          showFireTruckNormModal.value = true;
          return;
        }
      }
    }
    
    // Для всех остальных ошибок - показать в модали с автоскроллом
    const errorText = errorMsg || 'Произошла ошибка при обновлении записи';
    recordEditModal.value?.setValidationError(errorText);
  }
};

const openDeleteRecordsModal = () => {
  if (selectedRecordIds.value.length === 0) {
    noSelectionModal.value?.openModal();
    return;
  }
  const permissionKey = carType.value === 'fire-truck'
    ? 'can_delete_fire_truck_waybills_records'
    : 'can_delete_passenger_cars_waybills_records';
  
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

const openDeleteWaybillModal = () => {
  if (!auth.permissions.can_delete_fire_truck_waybills && !auth.permissions.can_delete_passenger_cars_waybills) {
    permissionDeniedModal.value?.openModal('can_delete_waybills');
    return;
  }
  showDeleteWaybillModal.value = true;
};

const closeDeleteWaybillModal = () => {
  showDeleteWaybillModal.value = false;
};

const confirmDeleteWaybill = async () => {
  try {
    const endpoint = carType.value === 'fire-truck'
      ? `fire-truck-waybills/${waybill.value.id}/`
      : `passenger-car-waybills/${waybill.value.id}/`;
    
    await axios.delete(endpoint, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[WaybillManagement] Waybill deleted successfully');
    closeDeleteWaybillModal();
    goBack();
  } catch (error) {
    console.error('Error deleting waybill:', error);
    errorModalRef.value?.openModal(error);
    closeDeleteWaybillModal();
  }
};

const goBack = () => {
  router.back();
};

const fetchRecordsWithPermissionCheck = async () => {
  if (!canViewRecords.value) {
    permissionDeniedModal.value?.openModal('view records');
    return;
  }
  await fetchRecords();
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: canCreateRecords.value,
    canDelete: canDeleteRecords.value
  });
};

// Odometer Modal Methods
const openOdometerFromEdit = () => {
  let carId = null;
  let carNumber = null;
  
  // Определяем какая машина редактируется
  if (carType.value === 'fire-truck' && editingFireTruck.value) {
    carId = editingFireTruck.value.id;
    carNumber = editingFireTruck.value.number;
    closeEditFireTruckModal();
  } else if (carType.value === 'passenger-car' && editingPassengerCar.value) {
    carId = editingPassengerCar.value.id;
    carNumber = editingPassengerCar.value.number;
    closeEditPassengerCarModal();
  }
  
  if (!carId) return;
  
  console.log(`[WaybillManagement] Opening odometer modal for car ${carNumber} (ID: ${carId})`);
  
  odometerData.value = {
    car: carId,
    odometer: '',
    fuel: '',
    date: new Date().toISOString().split('T')[0]
  };
  showOdometerModal.value = true;
};

const closeOdometerModal = () => {
  showOdometerModal.value = false;
  odometerData.value = {
    car: null,
    odometer: '',
    fuel: '',
    date: new Date().toISOString().split('T')[0]
  };
};

const handleOdometerSubmitted = async () => {
  console.log('[WaybillManagement] Odometer data saved successfully');
  // Перезагружаем данные машин чтобы обновить статус одометра
  await fetchCars();
  closeOdometerModal();
};

// Check if car has odometer
const hasOdometer = (carId) => {
  const car = cars.value.find(c => c.id === carId);
  return car && car.odometer_fuel_records && car.odometer_fuel_records.length > 0;
};

// Fire Truck Norm Handle
const handleNormAddSuccess = async () => {
  console.log('[WaybillManagement] Norm added successfully, retrying record save');
  showFireTruckNormModal.value = false;
  
  // Retry saving the pending record after a short delay
  setTimeout(async () => {
    if (recordEditModal.value && pendingRecordData.value) {
      if (pendingRecordData.value.id) {
        // It was an edit
        await handleEditRecord(pendingRecordData.value);
      } else {
        // It was an add
        await handleAddRecord(pendingRecordData.value);
      }
      pendingRecordData.value = null;
    }
  }, 500);
};

// Lifecycle
onMounted(async () => {
  setupCrudPermissions();
  const fetchTasks = [fetchWaybill(), fetchRecordsWithPermissionCheck(), fetchCars(), fetchDrivers()];
  
  await Promise.all(fetchTasks);
});

onUnmounted(() => {
  auth.clearCrudPermissions();
});
</script>
