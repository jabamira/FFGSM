<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Пожарные автомобили</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите гос. номер, марку или модель" class="mb-4" />
        <DataTable 
          :data="filteredFireTrucks" 
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
        <TextInput 
          v-model="newFireTruck.number" 
          :label="fieldDefinitions.fireTruck.number.label" 
          :hint="fieldDefinitions.fireTruck.number.hint"
          placeholder="Введите гос. номер"
          :required="fieldDefinitions.fireTruck.number.required"
        />
        <TextInput 
          v-model="newFireTruck.brand" 
          :label="fieldDefinitions.fireTruck.brand.label" 
          :hint="fieldDefinitions.fireTruck.brand.hint"
          placeholder="Введите марку"
          :required="fieldDefinitions.fireTruck.brand.required"
        />
        <TextInput 
          v-model="newFireTruck.model" 
          :label="fieldDefinitions.fireTruck.model.label" 
          :hint="fieldDefinitions.fireTruck.model.hint"
          placeholder="Введите модель"
          :required="fieldDefinitions.fireTruck.model.required"
        />
        <TextInput 
          v-model="newFireTruck.type" 
          :label="fieldDefinitions.fireTruck.type.label" 
          :hint="fieldDefinitions.fireTruck.type.hint"
          placeholder="Введите тип"
          :required="fieldDefinitions.fireTruck.type.required"
        />
        <SelectInput 
          v-model="newFireTruck.fuel_type" 
          :label="fieldDefinitions.fireTruck.fuel_type.label" 
          :hint="fieldDefinitions.fireTruck.fuel_type.hint"
          :options="fuelTypeOptions"
          placeholder="Выберите тип топлива"
          :required="fieldDefinitions.fireTruck.fuel_type.required"
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
    <Modal
      :is-open="showEditModal"
      title="Редактировать пожарный автомобиль"
      @close="closeEditModal"
    >
      <div v-if="editingFireTruck" class="space-y-4 min-w-96">
        <TextInput 
          v-model="editingFireTruck.number" 
          :label="fieldDefinitions.fireTruck.number.label" 
          :hint="fieldDefinitions.fireTruck.number.hint"
          placeholder="Введите гос. номер"
          :required="fieldDefinitions.fireTruck.number.required"
        />
        <TextInput 
          v-model="editingFireTruck.brand" 
          :label="fieldDefinitions.fireTruck.brand.label" 
          :hint="fieldDefinitions.fireTruck.brand.hint"
          placeholder="Введите марку"
          :required="fieldDefinitions.fireTruck.brand.required"
        />
        <TextInput 
          v-model="editingFireTruck.model" 
          :label="fieldDefinitions.fireTruck.model.label" 
          :hint="fieldDefinitions.fireTruck.model.hint"
          placeholder="Введите модель"
          :required="fieldDefinitions.fireTruck.model.required"
        />
        <TextInput 
          v-model="editingFireTruck.type" 
          :label="fieldDefinitions.fireTruck.type.label" 
          :hint="fieldDefinitions.fireTruck.type.hint"
          placeholder="Введите тип"
          :required="fieldDefinitions.fireTruck.type.required"
        />
        <SelectInput 
          v-model="editingFireTruck.fuel_type" 
          :label="fieldDefinitions.fireTruck.fuel_type.label" 
          :hint="fieldDefinitions.fireTruck.fuel_type.hint"
          :options="fuelTypeOptions"
          placeholder="Выберите тип топлива"
          :required="fieldDefinitions.fireTruck.fuel_type.required"
        />
      </div>
      <template #footer>
        <Button 
          v-if="editingFireTruck && !hasOdometer(editingFireTruck.id) && auth.permissions.view_fire_trucks"
          variant="secondary" 
          size="md" 
          @click="openOdometerFromEdit"
        >
          Внести стартовые данные
        </Button>
        <Button variant="secondary" size="md" @click="closeEditModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="updateFireTruck">Сохранить</Button>
      </template>
    </Modal>

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

const auth = useAuthStore();
const fireTrucks = ref([]);
const selectedFireTruckIds = ref([]);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const errorModalRef = ref(null);
const { searchQuery, filtered: filteredFireTrucks } = useSearch(fireTrucks, ['number', 'brand', 'model', 'type']);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);
const editingFireTruck = ref(null);
const originalFireTruck = ref(null);

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' },
  { key: 'type', label: 'Тип' },
  { key: 'fuel_type', label: 'Тип топлива' }
];

const newFireTruck = ref({
  number: '',
  brand: '',
  model: '',
  type: '',
  fuel_type: '',
});

const showOdometerModal = ref(false);
const isOdometerRequired = ref(true);
const odometerData = ref({
  car: null,
  odometer: '',
  fuel: '',
  date: new Date().toISOString().split('T')[0]
});

const fetchFireTrucks = async () => {
  if (!auth.permissions.view_fire_trucks) {
    console.warn('Нет разрешения на просмотр пожарных автомобилей (view_fire_trucks).');
    return;
  }

  try {
    const response = await axios.get('/fire-trucks/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fireTrucks.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке пожарных автомобилей:', error);
  }
};

const fireTrucksToDelete = computed(() => {
  return filteredFireTrucks.value.filter(t => selectedFireTruckIds.value.includes(t.id));
});

const getSelectedIndexes = () => {
  return filteredFireTrucks.value
    .map((truck, index) => selectedFireTruckIds.value.includes(truck.id) ? index : -1)
    .filter(index => index !== -1);
};

const onRowsSelected = (selectedIndexes) => {
  selectedFireTruckIds.value = selectedIndexes.map(idx => filteredFireTrucks.value[idx].id);
};

const openAddModal = () => {
  resetNewFireTruck();
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
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
  if (!auth.permissions.can_create_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_create_fire_trucks');
    closeAddModal();
    return;
  }

  const validationErrors = validateFormFields(newFireTruck.value, fieldDefinitions.fireTruck);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
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

const closeEditModal = () => {
  showEditModal.value = false;
  editingFireTruck.value = null;
  originalFireTruck.value = null;
};

const hasFireTruckChanged = () => {
  if (!editingFireTruck.value || !originalFireTruck.value) return false;
  return JSON.stringify(editingFireTruck.value) !== JSON.stringify(originalFireTruck.value);
};

const updateFireTruck = async () => {
  if (!auth.permissions.can_update_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_update_fire_trucks');
    closeEditModal();
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
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
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
  return truck && truck.odometer_fuel_fire_trucks && truck.odometer_fuel_fire_trucks.length > 0;
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

const handleOdometerSubmitted = () => {
  showOdometerModal.value = false;
  isOdometerRequired.value = true;
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

onMounted(() => {
  console.debug("[FireTrucks] Permissions loaded from store:", auth.permissions);
  setupCrudPermissions();
  
  if (auth.permissions.view_fire_trucks) {
    fetchFireTrucks();
  } else {
    console.warn("[FireTrucks] User does not have permission to view fire trucks.");
  }
});

onUnmounted(() => {
  auth.clearCrudPermissions();
});
</script>
