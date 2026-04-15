<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Пожарные автомобили</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <div>
            <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите гос. номер, марку или модель" />
          </div>
          <div>
            <SelectInput 
              v-model="filterFuelType" 
              label="Тип топлива"
              :options="fuelsFilterOptions"
              placeholder="Все типы"
            />
          </div>
        </div>
        <DataTable 
          :data="finalFilteredFireTrucks" 
          :columns="columns"
          :selectable="true"
          :show-select-all="false"
          :selected-rows="getSelectedIndexes()"
          @row-selected="onRowsSelected"
          @row-click="onRowClick"
        >
          <template #cell-fuel_type="{ row }">
            {{ formatFuelType(row.fuel_type) }}
          </template>
          <template #cell-hours_until_maintenance="{ row }">
            <div @click.stop class="w-full">
              <Button 
                @click="openMaintenanceModal(row)"
                :style="getMaintenanceStyle(row)"
                variant="secondary"
                size="sm"
                class="w-full"
              >
                {{ formatMaintenanceHours(row) }}
              </Button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Modal добавления пожарной машины -->
    <Modal
      :is-open="showAddModal"
      title="Создать пожарный автомобиль"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <div v-if="addFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ addFormGeneralError }}</p>
        </div>
        <TextInput 
          v-model="newFireTruck.number" 
          :label="fieldDefinitions.fireTruck.number.label" 
          :hint="fieldDefinitions.fireTruck.number.hint"
          placeholder="Введите гос. номер"
          :required="fieldDefinitions.fireTruck.number.required"
          :uppercase="fieldDefinitions.fireTruck.number.uppercase"
          :error="addFormErrors.number"
        />
        <TextInput 
          v-model="newFireTruck.brand" 
          :label="fieldDefinitions.fireTruck.brand.label" 
          :hint="fieldDefinitions.fireTruck.brand.hint"
          placeholder="Введите марку"
          :required="fieldDefinitions.fireTruck.brand.required"
          :error="addFormErrors.brand"
        />
        <TextInput 
          v-model="newFireTruck.model" 
          :label="fieldDefinitions.fireTruck.model.label" 
          :hint="fieldDefinitions.fireTruck.model.hint"
          placeholder="Введите модель"
          :required="fieldDefinitions.fireTruck.model.required"
          :error="addFormErrors.model"
        />
        <TextInput 
          v-model="newFireTruck.type" 
          :label="fieldDefinitions.fireTruck.type.label" 
          :hint="fieldDefinitions.fireTruck.type.hint"
          placeholder="Введите тип"
          :required="fieldDefinitions.fireTruck.type.required"
          :error="addFormErrors.type"
        />
        <SelectInput 
          v-model="newFireTruck.fuel_type" 
          :label="fieldDefinitions.fireTruck.fuel_type.label" 
          :hint="fieldDefinitions.fireTruck.fuel_type.hint"
          :options="fuelTypeOptions"
          placeholder="Выберите тип топлива"
          :required="fieldDefinitions.fireTruck.fuel_type.required"
          :error="addFormErrors.fuel_type"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeAddModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="addFireTruck">Добавить</Button>
      </template>
    </Modal>

    <!-- Modal подтверждения удаления -->
    <Modal
      :is-open="showDeleteModal"
      title="Подтвердить удаление"
      @close="closeDeleteModal"
    >
      <div class="space-y-4">
        <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующие пожарные автомобили:</p>
        <div class="bg-red-50 border border-red-200 rounded p-4">
          <ul class="space-y-2">
            <li v-for="truck in fireTrucksToDelete" :key="truck.id" :style="{ color: palette.dark }">
              {{ truck.number }} - {{ truck.brand }} {{ truck.model }}
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeDeleteModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="confirmDelete">Удалить</Button>
      </template>
    </Modal>

    <!-- Modal редактирования пожарной машины -->
    <FireTruckEditModal
      ref="firetruckEditModalRef"
      :is-open="showEditModal"
      :truck="editingFireTruck"
      :original-truck="originalFireTruck"
      :has-odometer="editingFireTruck ? hasOdometer(editingFireTruck.id) : false"
      :can-view-fire-trucks="auth.permissions.view_fire_trucks"
      @close="closeEditModal"
      @save="handleEditSave"
      @odometer-click="openOdometerFromEdit"
    />

    <!-- Modal внесения стартовых данных -->
    <OdometerModal
      :is-open="showOdometerModal"
      :car-id="odometerData.car"
      car-type="fire-truck"
      :is-required="isOdometerRequired"
      title="Внесение стартовых данных о пожарной машине"
      @close="closeOdometerModal"
      @submitted="handleOdometerSubmitted"
      @skipped="closeOdometerModal"
    />

    <!-- Permission Denied Modal -->
    <PermissionDeniedModal ref="permissionDeniedModal" />

    <!-- No Selection Modal -->
    <NoSelectionModal ref="noSelectionModal" />

    <!-- Error Modal -->
    <ErrorModal ref="errorModalRef" />

    <!-- Technical Maintenance Modal -->
    <TechnicalMaintenanceModal 
      :is-open="showMaintenanceModal"
      :truck="selectedMaintenanceTruck"
      :maintenance-info="selectedMaintenanceInfo"
      @close="closeMaintenanceModal"
      @success="handleMaintenanceSuccess"
    />

    <!-- CRUD Panel -->
    <CrudPanel 
      @create="handleCrudCreate"
      @delete="handleCrudDelete"
      createLabel="Создать автомобиль"
      :deleteLabel="deleteButtonLabel"
      :isDeleteDisabled="isDeleteDisabled"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { DataTable, TextInput, SelectInput, palette, Modal, Button } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import { useSearch } from '../composables/useSearch';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { fuelTypeOptions, formatFuelType } from '../config/fuelTypes';
import { validateFormFields, createValidationError } from '../utils/errorUtils';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import NoSelectionModal from '../components/NoSelectionModal.vue';
import CrudPanel from '../components/CrudPanel.vue';
import ErrorModal from '../components/ErrorModal.vue';
import OdometerModal from '../components/OdometerModal.vue';
import FireTruckEditModal from '../components/FireTruckEditModal.vue';
import TechnicalMaintenanceModal from '../components/TechnicalMaintenanceModal.vue';

const auth = useAuthStore();
const fireTrucks = ref([]);
const selectedFireTruckIds = ref([]);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const errorModalRef = ref(null);
const firetruckEditModalRef = ref(null);
const { searchQuery, filtered: filteredFireTrucks } = useSearch(fireTrucks, ['number', 'brand', 'model', 'type']);
const filterFuelType = ref('');
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);
const editingFireTruck = ref(null);
const originalFireTruck = ref(null);

const finalFilteredFireTrucks = computed(() => {
  let filtered = filteredFireTrucks.value;
  if (filterFuelType.value) {
    filtered = filtered.filter(truck => truck.fuel_type === filterFuelType.value);
  }
  return filtered;
});

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' },
  { key: 'type', label: 'Тип' },
  { key: 'fuel_type', label: 'Тип топлива' },
  { key: 'hours_until_maintenance', label: 'Часов до ТО' }
];

const newFireTruck = ref({
  number: '',
  brand: '',
  model: '',
  type: '',
  fuel_type: '',
});

const addFormErrors = ref({});
const editFormErrors = ref({});
const addFormGeneralError = ref('');
const editFormGeneralError = ref('');

const showOdometerModal = ref(false);
const isOdometerRequired = ref(true);
const odometerData = ref({
  car: null,
  odometer: '',
  fuel: '',
  date: new Date().toISOString().split('T')[0]
});

const showMaintenanceModal = ref(false);
const selectedMaintenanceTruck = ref(null);
const selectedMaintenanceInfo = ref(null);

const fetchFireTrucks = async () => {
  if (!auth.permissions.view_fire_trucks) {
    console.warn('Нет разрешения на просмотр пожарных автомобилей (view_fire_trucks).');
    return;
  }

  try {
    const response = await axios.get('/fire-trucks/?include_odometer=true&include_all_maintenance_info=true', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    // Для каждой машины выбираем самую критическую норму (с минимальным interval)
    fireTrucks.value = response.data.map(truck => {
      if (truck.all_maintenance_info && truck.all_maintenance_info.items && truck.all_maintenance_info.items.length > 0) {
        // Находим вид ТО с наименьшим количеством часов до срока
        const criticalMaintenance = truck.all_maintenance_info.items.reduce((min, current) => {
          return current.interval < min.interval ? current : min;
        });
        // Используем критическую норму как основную maintenance_info
        truck.maintenance_info = criticalMaintenance;
      }
      return truck;
    });
  } catch (error) {
    console.error('Ошибка при загрузке пожарных автомобилей:', error);
  }
};

const fuelsFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все типы' },
    ...fuelTypeOptions
  ];
});

const fireTrucksToDelete = computed(() => {
  return finalFilteredFireTrucks.value.filter(t => selectedFireTruckIds.value.includes(t.id));
});

const getSelectedIndexes = () => {
  return finalFilteredFireTrucks.value
    .map((truck, index) => selectedFireTruckIds.value.includes(truck.id) ? index : -1)
    .filter(index => index !== -1);
};

const onRowsSelected = (selectedIndexes) => {
  selectedFireTruckIds.value = selectedIndexes.map(idx => finalFilteredFireTrucks.value[idx].id);
};

const openAddModal = () => {
  resetNewFireTruck();
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  addFormErrors.value = {};
  addFormGeneralError.value = '';
  resetNewFireTruck();
};

const resetNewFireTruck = () => {
  newFireTruck.value = {
    number: '',
    brand: '',
    model: '',
    type: '',
    fuel_type: '',
  };
};

const addFireTruck = async () => {
  addFormGeneralError.value = '';
  addFormErrors.value = {};
  
  if (!auth.permissions.can_create_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_create_fire_trucks');
    return;
  }

  const validationErrors = validateFormFields(newFireTruck.value, fieldDefinitions.fireTruck);
  if (Object.keys(validationErrors).length > 0) {
    addFormErrors.value = validationErrors;
    addFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  try {
    const response = await axios.post('/fire-trucks/', newFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[FireTrucks] Fire truck added successfully:', response.data);
    fireTrucks.value.push(response.data);
    
    // Открываем модал для ввода стартовых данных
    odometerData.value.car = response.data.id;
    odometerData.value.date = new Date().toISOString().split('T')[0];
    isOdometerRequired.value = true;
    closeAddModal();
    showOdometerModal.value = true;
  } catch (error) {
    console.error('Ошибка при добавлении пожарного автомобиля:', error);
    addFormGeneralError.value = error.response?.data?.detail || error.message || 'Ошибка при добавлении пожарного автомобиля';
    errorModalRef.value?.openModal(error);
  }
};

const onRowClick = (truck) => {
  const canUpdateFireTrucks = auth.permissions.can_update_fire_trucks;

  if (!canUpdateFireTrucks) {
    permissionDeniedModal.value?.openModal('can_update_fire_trucks');
    return;
  }

  openEditModal(truck);
};

const openEditModal = (truck) => {
  originalFireTruck.value = { ...truck };
  editingFireTruck.value = { ...truck };
  showEditModal.value = true;
};

const handleEditSave = async () => {
  // Получить отредактированные данные из компонента
  if (firetruckEditModalRef.value) {
    editingFireTruck.value = firetruckEditModalRef.value.getTruck();
  }
  
  // Вызвать стандартное сохранение
  await updateFireTruck();
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingFireTruck.value = null;
  originalFireTruck.value = null;
  firetruckEditModalRef.value?.clearErrors();
};

const hasFireTruckChanged = () => {
  if (!editingFireTruck.value || !originalFireTruck.value) return false;
  return JSON.stringify(editingFireTruck.value) !== JSON.stringify(originalFireTruck.value);
};

const updateFireTruck = async () => {
  firetruckEditModalRef.value?.clearErrors();
  
  if (!auth.permissions.can_update_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_update_fire_trucks');
    return;
  }

  if (!editingFireTruck.value) return;

  if (!hasFireTruckChanged()) {
    console.log('[FireTrucks] No changes detected');
    closeEditModal();
    return;
  }

  const validationErrors = validateFormFields(editingFireTruck.value, fieldDefinitions.fireTruck);
  if (Object.keys(validationErrors).length > 0) {
    firetruckEditModalRef.value?.setErrors(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    return;
  }

  try {
    const response = await axios.put(`/fire-trucks/${editingFireTruck.value.id}/`, editingFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[FireTrucks] Fire truck updated successfully:', response.data);
    
    const truckIndex = fireTrucks.value.findIndex(t => t.id === editingFireTruck.value.id);
    if (truckIndex > -1) {
      fireTrucks.value[truckIndex] = response.data;
    }
    
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при обновлении пожарного автомобиля:', error);
    editFormGeneralError.value = error.response?.data?.detail || error.message || 'Ошибка при обновлении пожарного автомобиля';
    errorModalRef.value?.openModal(error);
  }
};

const openDeleteModal = () => {
  if (selectedFireTruckIds.value.length === 0) {
    noSelectionModal.value?.openModal();
    return;
  }
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const confirmDelete = async () => {
  if (!auth.permissions.can_delete_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_delete_fire_trucks');
    closeDeleteModal();
    return;
  }

  try {
    for (const id of selectedFireTruckIds.value) {
      await axios.delete(`/fire-trucks/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[FireTrucks] Fire trucks deleted successfully');
    
    selectedFireTruckIds.value = [];
    await fetchFireTrucks();
    closeDeleteModal();
  } catch (error) {
    console.error('Ошибка при удалении пожарных автомобилей:', error);
    errorModalRef.value?.openModal(error);
  }
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

const submitOdometerData = async () => {
  try {
    const payload = {
      car: odometerData.value.car,
      odometer: parseInt(odometerData.value.odometer),
      fuel: parseFloat(odometerData.value.fuel),
      date: odometerData.value.date
    };

    await axios.post('/fire-truck-odometer-fuel/', payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });

    console.log('[FireTrucks] Odometer data saved successfully');
    closeOdometerModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных одометра:', error);
    errorModalRef.value?.openModal(error);
  }
};

const hasOdometer = (carId) => {
  const truck = fireTrucks.value.find(t => t.id === carId);
  return truck && truck.odometer_fuel_records && truck.odometer_fuel_records.length > 0;
};

const openOdometerFromEdit = () => {
  if (!editingFireTruck.value) return;
  
  const carId = editingFireTruck.value.id;
  closeEditModal();
  odometerData.value.car = carId;
  odometerData.value.date = new Date().toISOString().split('T')[0];
  isOdometerRequired.value = false;
  showOdometerModal.value = true;
};

const handleOdometerSubmitted = async () => {
  showOdometerModal.value = false;
  isOdometerRequired.value = true;
  
  // Перезагружаем данные машин чтобы обновить статус одометра
  await fetchFireTrucks();
  
  // Закрываем окно редактирования
  closeEditModal();
  closeOdometerModal();
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_fire_trucks || false,
    canDelete: auth.permissions.can_delete_fire_trucks || false,
  });
};

const handleCrudCreate = () => {
  openAddModal();
};

const deleteButtonLabel = computed(() => {
  const count = selectedFireTruckIds.value.length;
  if (count === 0) return 'Удалить автомобиль';
  if (count === 1) return 'Удалить автомобиль';
  return `Удалить автомобилей (${count})`;
});

const isDeleteDisabled = computed(() => selectedFireTruckIds.value.length === 0);

const handleCrudDelete = () => {
  openDeleteModal();
};

const formatMaintenanceHours = (row) => {
  // Проверка наличия информации о ТО
  if (!row.maintenance_info || row.maintenance_info?.error) {
    return 'нет норм';
  }
  
  const maintenanceType = row.maintenance_info?.maintenance_type || 'ТО';
  const hours = row.maintenance_info?.interval;  // Используем interval из maintenance_info
  
  if (hours === null || hours === undefined) {
    return `${maintenanceType}: нет данных`;
  }
  
  // Если ТО уже должна была пройти
  if (hours < 0) {
    const overdueHours = Math.abs(hours).toFixed(2);
    return `${maintenanceType}: должно было ${overdueHours} ч назад`;
  }
  
  if (hours < 10) {
    return `${maintenanceType}: ${hours.toFixed(2)} ч ⚠️`;
  }
  
  return `${maintenanceType}: ${hours.toFixed(2)} ч`;
};

const getMaintenanceStyle = (row) => {
  // Проверка наличия информации о ТО - если нет норм, серый цвет
  if (!row.maintenance_info || row.maintenance_info?.error) {
    return {
      color: palette.medium,
      backgroundColor: palette.light + '30и в',
      padding: '6px 12px',
      borderRadius: '4px',
      textAlign: 'center',
      fontSize: '0.9em',
      border: `1px solid ${palette.light}`
    };
  }
  
  const hours = row.maintenance_info?.interval;  // Используем interval из maintenance_info
  
  if (hours === null || hours === undefined) {
    return {
      color: palette.medium,
      backgroundColor: palette.light + '30',
      padding: '6px 12px',
      borderRadius: '4px',
      textAlign: 'center',
      fontSize: '0.9em',
      border: `1px solid ${palette.light}`
    };
  }
  
  // Красная: уже должна была пройти или < 10 часов
  if (hours < 10) {
    return {
      color: '#fff',
      fontWeight: 'bold',
      backgroundColor: '#ef4444',
      padding: '6px 12px',
      borderRadius: '4px',
      textAlign: 'center'
    };
  }
  
  // Оранжевая: 10-50 часов - ТО в ближайшее время
  if (hours < 50) {
    return {
      color: '#fff',
      fontWeight: 'bold',
      backgroundColor: '#f97316',
      padding: '6px 12px',
      borderRadius: '4px',
      textAlign: 'center'
    };
  }
  
  // Зелёная: >= 50 часов - достаточно времени
  return {
    color: '#fff',
    fontWeight: 'bold',
    backgroundColor: '#10b981',
    padding: '6px 12px',
    borderRadius: '4px',
    textAlign: 'center'
  };
};

const openMaintenanceModal = async (truck) => {
  try {
    // Получить свежие данные машины с информацией по всем видам ТО
    // Добавляем timestamp для предотвращения кеширования и получения актуальных operating_hours
    const timestamp = Date.now();
    const response = await axios.get(`/fire-trucks/${truck.id}/?include_all_maintenance_info=true&t=${timestamp}`, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    const freshTruck = response.data;
    console.log('[FireTrucks] Свежие данные с сервера:', freshTruck);
    
    if (!freshTruck.all_maintenance_info || freshTruck.all_maintenance_info?.error) {
      console.warn('Информация о ТО недоступна для этой машины');
      return;
    }
    
    selectedMaintenanceTruck.value = freshTruck;
    // Передаем ALL виды ТО в модал, а не только одну норму
    selectedMaintenanceInfo.value = freshTruck.all_maintenance_info;
    showMaintenanceModal.value = true;
  } catch (error) {
    console.error('[FireTrucks] Ошибка при загрузке данных для модала ТО:', error);
    errorModalRef.value?.openModal(error);
  }
};

const closeMaintenanceModal = () => {
  showMaintenanceModal.value = false;
  selectedMaintenanceTruck.value = null;
  selectedMaintenanceInfo.value = null;
};

const handleMaintenanceSuccess = async () => {
  // Перезагружаем данные машин
  await fetchFireTrucks();
  closeMaintenanceModal();
};

onMounted(() => {
  console.debug("[FireTrucks] Permissions loaded from store:", auth.permissions);
  setupCrudPermissions();
  
  if (auth.permissions.view_fire_trucks) {
    fetchFireTrucks();
  } else {
    console.warn("[FireTrucks] User does not have permission to view fire trucks.");
    permissionDeniedModal.value?.openModal('view_fire_trucks');
  }
});

onUnmounted(() => {
  auth.clearCrudPermissions();
});
</script>
