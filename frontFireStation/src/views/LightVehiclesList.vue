<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Легковые автомобили</h2>
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
          :data="finalFilteredPassengerCars" 
          :columns="columns"
          :selectable="true"
          :show-select-all="false"
          :selected-rows="selectedPassengerCarIds"
          @row-selected="onRowsSelected"
          @row-click="onRowClick"
          row-id-key="id"
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

    <!-- Modal добавления легкового автомобиля -->
    <Modal
      :is-open="showAddModal"
      title="Создать легковой автомобиль"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <div v-if="addFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ addFormGeneralError }}</p>
        </div>
        <TextInput 
          v-model="newPassengerCar.number" 
          :label="fieldDefinitions.passengerCar.number.label" 
          :hint="fieldDefinitions.passengerCar.number.hint"
          :error="addFormErrors.number"
          placeholder="Введите гос. номер"
          :required="fieldDefinitions.passengerCar.number.required"
          :uppercase="fieldDefinitions.passengerCar.number.uppercase"
        />
        <TextInput 
          v-model="newPassengerCar.brand" 
          :label="fieldDefinitions.passengerCar.brand.label" 
          :hint="fieldDefinitions.passengerCar.brand.hint"
          :error="addFormErrors.brand"
          placeholder="Введите марку"
          :required="fieldDefinitions.passengerCar.brand.required"
        />
        <TextInput 
          v-model="newPassengerCar.model" 
          :label="fieldDefinitions.passengerCar.model.label" 
          :hint="fieldDefinitions.passengerCar.model.hint"
          :error="addFormErrors.model"
          placeholder="Введите модель"
          :required="fieldDefinitions.passengerCar.model.required"
        />
        <SelectInput 
          v-model="newPassengerCar.fuel_type" 
          :label="fieldDefinitions.passengerCar.fuel_type.label" 
          :hint="fieldDefinitions.passengerCar.fuel_type.hint"
          :error="addFormErrors.fuel_type"
          :options="fuelTypeOptions"
          placeholder="Выберите тип топлива"
          :required="fieldDefinitions.passengerCar.fuel_type.required"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeAddModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="addPassengerCar">Добавить</Button>
      </template>
    </Modal>

    <!-- Modal подтверждения удаления -->
    <Modal
      :is-open="showDeleteModal"
      title="Подтвердить удаление"
      @close="closeDeleteModal"
    >
      <div class="space-y-4">
        <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующие легковые автомобили:</p>
        <div class="bg-red-50 border border-red-200 rounded p-4">
          <ul class="space-y-2">
            <li v-for="car in passengerCarsToDelete" :key="car.id" :style="{ color: palette.dark }">
              {{ car.number }} - {{ car.brand }} {{ car.model }}
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeDeleteModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="confirmDelete">Удалить</Button>
      </template>
    </Modal>

    <!-- Modal редактирования легкового автомобиля -->
    <PassengerCarEditModal
      ref="passengerCarEditModalRef"
      :is-open="showEditModal"
      :car="editingPassengerCar"
      :original-car="originalPassengerCar"
      :has-odometer="editingPassengerCar ? hasOdometer(editingPassengerCar.id) : false"
      :can-view-passenger-cars="auth.permissions.view_passenger_cars"
      @close="closeEditModal"
      @save="handleEditSave"
      @odometer-click="openOdometerFromEdit"
    />

    <!-- Modal внесения стартовых данных -->
    <OdometerModal
      :is-open="showOdometerModal"
      :car-id="odometerData.car"
      car-type="passenger-car"
      :is-required="isOdometerRequired"
      title="Внесение стартовых данных о легковой машине"
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
      :car="selectedMaintenanceCar"
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
import PassengerCarEditModal from '../components/PassengerCarEditModal.vue';
import TechnicalMaintenanceModal from '../components/TechnicalMaintenanceModal.vue';

const auth = useAuthStore();
const passengerCars = ref([]);
const selectedPassengerCarIds = ref([]);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const errorModalRef = ref(null);
const passengerCarEditModalRef = ref(null);
const { searchQuery, filtered: filteredPassengerCars } = useSearch(passengerCars, ['number', 'brand', 'model']);
const filterFuelType = ref('');
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);
const editingPassengerCar = ref(null);
const originalPassengerCar = ref(null);

const finalFilteredPassengerCars = computed(() => {
  let filtered = filteredPassengerCars.value;
  if (filterFuelType.value) {
    filtered = filtered.filter(car => car.fuel_type === filterFuelType.value);
  }
  return filtered;
});

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' },
  { key: 'fuel_type', label: 'Тип топлива' },
  { key: 'hours_until_maintenance', label: 'Часов до ТО' }
];

const newPassengerCar = ref({
  number: '',
  brand: '',
  model: '',
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
const selectedMaintenanceCar = ref(null);
const selectedMaintenanceInfo = ref(null);

const fetchPassengerCars = async () => {
  if (!auth.permissions.view_passenger_cars) {
    console.warn('Нет разрешения на просмотр легковых автомобилей (view_passenger_cars).');
    return;
  }

  try {
    const response = await axios.get('/passenger-cars/?include_odometer=true&include_all_maintenance_info=true', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    // Для каждой машины выбираем самую критическую норму (с минимальным interval)
    passengerCars.value = response.data.map(car => {
      if (car.all_maintenance_info && car.all_maintenance_info.items && car.all_maintenance_info.items.length > 0) {
        // Обогащаем каждую ТО вычисленными значениями
        const enrichedItems = car.all_maintenance_info.items.map(item => {
          const currentHours = Number(car.operating_hours) || 0;
          const lastMaintenanceHours = Number(item.last_maintenance_hours) || 0;
          const normIntervalValue = Number(item.norm_interval_value) || 0;
          
          return {
            ...item,
            interval: (lastMaintenanceHours + normIntervalValue) - currentHours,
            next_maintenance_at: lastMaintenanceHours + normIntervalValue,
            previous_maintenance_hours: lastMaintenanceHours
          };
        });
        
        // Находим вид ТО с наименьшим количеством часов до срока
        const criticalMaintenance = enrichedItems.reduce((min, current) => {
          return current.interval < min.interval ? current : min;
        });
        
        // Используем критическую норму как основную maintenance_info
        car.maintenance_info = criticalMaintenance;
      }
      return car;
    });
  } catch (error) {
    console.error('Ошибка при загрузке легковых автомобилей:', error);
  }
};

const fuelsFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все типы' },
    ...fuelTypeOptions
  ];
});

const passengerCarsToDelete = computed(() => {
  return finalFilteredPassengerCars.value.filter(c => selectedPassengerCarIds.value.includes(c.id));
});

const onRowsSelected = (selectedIds) => {
  selectedPassengerCarIds.value = selectedIds;
};

const openAddModal = () => {
  resetNewPassengerCar();
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  resetNewPassengerCar();
  addFormErrors.value = {};
  addFormGeneralError.value = '';
};

const resetNewPassengerCar = () => {
  newPassengerCar.value = {
    number: '',
    brand: '',
    model: '',
    fuel_type: '',
  };
};

const addPassengerCar = async () => {
  addFormGeneralError.value = '';
  addFormErrors.value = {};

  if (!auth.permissions.can_create_passenger_cars) {
    permissionDeniedModal.value?.openModal('can_create_passenger_cars');
    closeAddModal();
    return;
  }

  const validationErrors = validateFormFields(newPassengerCar.value, fieldDefinitions.passengerCar);
  if (Object.keys(validationErrors).length > 0) {
    addFormErrors.value = validationErrors;
    addFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  try {
    const response = await axios.post('/passenger-cars/', newPassengerCar.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[PassengerCars] Passenger car added successfully:', response.data);
    passengerCars.value.push(response.data);
    
    // Открываем модал для ввода стартовых данных
    odometerData.value.car = response.data.id;
    odometerData.value.date = new Date().toISOString().split('T')[0];
    isOdometerRequired.value = true;
    closeAddModal();
    showOdometerModal.value = true;
  } catch (error) {
    console.error('Ошибка при добавлении легкового автомобиля:', error);
    errorModalRef.value?.openModal(error);
  }
};

const onRowClick = (car) => {
  const canUpdatePassengerCars = auth.permissions.can_update_passenger_cars;

  if (!canUpdatePassengerCars) {
    permissionDeniedModal.value?.openModal('can_update_passenger_cars');
    return;
  }

  openEditModal(car);
};

const openEditModal = (car) => {
  originalPassengerCar.value = { ...car };
  editingPassengerCar.value = { ...car };
  showEditModal.value = true;
};

const handleEditSave = async () => {
  // Получить отредактированные данные из компонента
  if (passengerCarEditModalRef.value) {
    editingPassengerCar.value = passengerCarEditModalRef.value.getCar();
  }
  
  // Вызвать стандартное сохранение
  await updatePassengerCar();
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingPassengerCar.value = null;
  originalPassengerCar.value = null;
  passengerCarEditModalRef.value?.clearErrors();
};

const hasPassengerCarChanged = () => {
  if (!editingPassengerCar.value || !originalPassengerCar.value) return false;
  return JSON.stringify(editingPassengerCar.value) !== JSON.stringify(originalPassengerCar.value);
};

const updatePassengerCar = async () => {
  passengerCarEditModalRef.value?.clearErrors();

  if (!auth.permissions.can_update_passenger_cars) {
    permissionDeniedModal.value?.openModal('can_update_passenger_cars');
    closeEditModal();
    return;
  }

  if (!editingPassengerCar.value) return;

  if (!hasPassengerCarChanged()) {
    console.log('[PassengerCars] No changes detected');
    closeEditModal();
    return;
  }

  const validationErrors = validateFormFields(editingPassengerCar.value, fieldDefinitions.passengerCar);
  if (Object.keys(validationErrors).length > 0) {
    passengerCarEditModalRef.value?.setErrors(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    return;
  }

  try {
    const response = await axios.put(`/passenger-cars/${editingPassengerCar.value.id}/`, editingPassengerCar.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[PassengerCars] Passenger car updated successfully:', response.data);
    
    const carIndex = passengerCars.value.findIndex(c => c.id === editingPassengerCar.value.id);
    if (carIndex > -1) {
      passengerCars.value[carIndex] = response.data;
    }
    
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при обновлении легкового автомобиля:', error);
    errorModalRef.value?.openModal(error);
  }
};

const openDeleteModal = () => {
  if (selectedPassengerCarIds.value.length === 0) {
    noSelectionModal.value?.openModal();
    return;
  }
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const confirmDelete = async () => {
  if (!auth.permissions.can_delete_passenger_cars) {
    permissionDeniedModal.value?.openModal('can_delete_passenger_cars');
    closeDeleteModal();
    return;
  }

  try {
    for (const id of selectedPassengerCarIds.value) {
      await axios.delete(`/passenger-cars/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[PassengerCars] Passenger cars deleted successfully');
    
    selectedPassengerCarIds.value = [];
    await fetchPassengerCars();
    closeDeleteModal();
  } catch (error) {
    console.error('Ошибка при удалении легковых автомобилей:', error);
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

    await axios.post('/passenger-car-odometer-fuel/', payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });

    console.log('[PassengerCars] Odometer data saved successfully');
    closeOdometerModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных одометра:', error);
    errorModalRef.value?.openModal(error);
  }
};

const hasOdometer = (carId) => {
  const car = passengerCars.value.find(c => c.id === carId);
  return car && car.odometer_fuel_records && car.odometer_fuel_records.length > 0;
};

const openOdometerFromEdit = () => {
  if (!editingPassengerCar.value) return;
  
  const carId = editingPassengerCar.value.id;
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
  await fetchPassengerCars();
  
  // Закрываем окно редактирования
  closeEditModal();
  closeOdometerModal();
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_passenger_cars || false,
    canDelete: auth.permissions.can_delete_passenger_cars || false,
  });
};

const handleCrudCreate = () => {
  openAddModal();
};

const deleteButtonLabel = computed(() => {
  const count = selectedPassengerCarIds.value.length;
  if (count === 0) return 'Удалить автомобиль';
  if (count === 1) return 'Удалить автомобиль';
  return `Удалить автомобилей (${count})`;
});

const isDeleteDisabled = computed(() => selectedPassengerCarIds.value.length === 0);

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
      backgroundColor: palette.light + '30',
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

const openMaintenanceModal = async (car) => {
  try {
    // Получить свежие данные машины с информацией по всем видам ТО
    // Добавляем timestamp для предотвращения кеширования и получения актуальных operating_hours
    const timestamp = Date.now();
    const response = await axios.get(`/passenger-cars/${car.id}/?include_all_maintenance_info=true&t=${timestamp}`, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    const freshCar = response.data;
    console.log('[PassengerCars] Свежие данные с сервера:', freshCar);
    
    if (!freshCar.all_maintenance_info || freshCar.all_maintenance_info?.error) {
      console.warn('Информация о ТО недоступна для этой машины');
      return;
    }
    
    // Обогащаем каждую ТО вычисленными значениями
    if (freshCar.all_maintenance_info.items && freshCar.all_maintenance_info.items.length > 0) {
      const enrichedItems = freshCar.all_maintenance_info.items.map(item => {
        const currentHours = Number(freshCar.operating_hours) || 0;
        const lastMaintenanceHours = Number(item.last_maintenance_hours) || 0;
        const normIntervalValue = Number(item.norm_interval_value) || 0;
        
        const enriched = {
          ...item,
          interval: (lastMaintenanceHours + normIntervalValue) - currentHours,
          next_maintenance_at: lastMaintenanceHours + normIntervalValue,
          previous_maintenance_hours: lastMaintenanceHours
        };
        
        console.log('[PassengerCars] Обогащение ТО:', {
          maintenance_type: item.maintenance_type,
          currentHours,
          lastMaintenanceHours,
          normIntervalValue,
          enriched
        });
        
        return enriched;
      });
      freshCar.all_maintenance_info.items = enrichedItems;
    }
    
    selectedMaintenanceCar.value = freshCar;
    // Передаем ALL виды ТО в модал, а не только одну норму
    selectedMaintenanceInfo.value = freshCar.all_maintenance_info;
    showMaintenanceModal.value = true;
  } catch (error) {
    console.error('[PassengerCars] Ошибка при загрузке данных для модала ТО:', error);
    errorModalRef.value?.openModal(error);
  }
};

const closeMaintenanceModal = () => {
  showMaintenanceModal.value = false;
  selectedMaintenanceCar.value = null;
  selectedMaintenanceInfo.value = null;
};

const handleMaintenanceSuccess = async (responseData) => {
  // 🔴 Обновляем конкретную машину с новыми operating_hours
  // После проведения ТО получаем свежие данные этой машины
  if (selectedMaintenanceCar.value?.id) {
    try {
      const carId = selectedMaintenanceCar.value.id;
      const timestamp = Date.now();
      const response = await axios.get(`/passenger-cars/${carId}/?include_all_maintenance_info=true&t=${timestamp}`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
      
      const updatedCar = response.data;
      console.log('[PassengerCars] ТО проведено! Обновленные данные машины:', updatedCar);
      
      // Обновляем эту машину в списке
      const idx = passengerCars.value.findIndex(c => c.id === carId);
      if (idx !== -1) {
        passengerCars.value[idx] = updatedCar;
      }
    } catch (error) {
      console.error('[PassengerCars] Ошибка при обновлении машины после ТО:', error);
      // В случае ошибки перезагружаем все машины
      await fetchPassengerCars();
    }
  }
  
  closeMaintenanceModal();
};

onMounted(() => {
  console.debug("[PassengerCars] Permissions loaded from store:", auth.permissions);
  setupCrudPermissions();
  
  if (auth.permissions.view_passenger_cars) {
    fetchPassengerCars();
  } else {
    console.warn("[PassengerCars] User does not have permission to view passenger cars.");
    permissionDeniedModal.value?.openModal('view_passenger_cars');
  }
});

onUnmounted(() => {
  auth.clearCrudPermissions();
});
</script>
