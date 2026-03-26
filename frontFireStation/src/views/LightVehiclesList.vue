<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Список легковых автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <template v-if="permissions.can_create_passenger_cars">
          <Button label="Добавить автомобиль" variant="primary" @click="openAddModal" class="mb-4" />
        </template>
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите данные для поиска" class="mb-4" />
        <DataTable :data="filteredPassengerCars" :columns="columns" @row-click="permissions.can_update_passenger_cars ? openEditModal : null">
          <template #actions="{ row }">
            <Button v-if="permissions.can_delete_passenger_cars" label="Удалить" variant="danger" @click="deletePassengerCar(row.id)" />
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Add Passenger Car Modal -->
    <Modal :is-open="isAddModalOpen" title="Добавить автомобиль" @close="closeAddModal">
      <form @submit.prevent="addPassengerCar">
        <div class="space-y-4 min-w-96">
          <TextInput 
            v-model="newPassengerCar.number" 
            :label="fieldDefinitions.passengerCar.number.label"
            :hint="fieldDefinitions.passengerCar.number.hint"
            placeholder="Гос. номер"
            :required="fieldDefinitions.passengerCar.number.required"
          />
          <TextInput 
            v-model="newPassengerCar.brand" 
            :label="fieldDefinitions.passengerCar.brand.label"
            :hint="fieldDefinitions.passengerCar.brand.hint"
            placeholder="Марка"
            :required="fieldDefinitions.passengerCar.brand.required"
          />
          <TextInput 
            v-model="newPassengerCar.model" 
            :label="fieldDefinitions.passengerCar.model.label"
            :hint="fieldDefinitions.passengerCar.model.hint"
            placeholder="Модель"
            :required="fieldDefinitions.passengerCar.model.required"
          />
        </div>
        <Button label="Сохранить" variant="primary" type="submit" />
      </form>
    </Modal>

    <!-- Edit Passenger Car Modal -->
    <Modal :is-open="isEditModalOpen" title="Редактировать данные" @close="closeEditModal">
      <form @submit.prevent="savePassengerCar">
        <div class="space-y-4 min-w-96">
          <TextInput 
            v-model="editablePassengerCar.number" 
            :label="fieldDefinitions.passengerCar.number.label"
            :hint="fieldDefinitions.passengerCar.number.hint"
            placeholder="Гос. номер"
            :required="fieldDefinitions.passengerCar.number.required"
          />
          <TextInput 
            v-model="editablePassengerCar.brand" 
            :label="fieldDefinitions.passengerCar.brand.label"
            :hint="fieldDefinitions.passengerCar.brand.hint"
            placeholder="Марка"
            :required="fieldDefinitions.passengerCar.brand.required"
          />
          <TextInput 
            v-model="editablePassengerCar.model" 
            :label="fieldDefinitions.passengerCar.model.label"
            :hint="fieldDefinitions.passengerCar.model.hint"
            placeholder="Модель"
            :required="fieldDefinitions.passengerCar.model.required"
          />
        </div>
        <Button label="Сохранить" variant="primary" type="submit" />
      </form>
    </Modal>

    <!-- Error Modal -->
    <ErrorModal ref="errorModalRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { DataTable, TextInput, Modal, Button, palette } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields, createValidationError } from '../utils/errorUtils';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';
import ErrorModal from '../components/ErrorModal.vue';

const auth = useAuthStore();
const errorModalRef = ref(null);
const passengerCars = ref([]);
const searchQuery = ref('');
const isAddModalOpen = ref(false);
const isEditModalOpen = ref(false);
const newPassengerCar = ref({ number: '', brand: '', model: '' });
const editablePassengerCar = ref({});
const permissions = computed(() => auth.permissions);

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' },
  { key: 'actions', label: 'Действия', slot: true }
];

const fetchPassengerCars = async () => {
  if (!permissions.value.view_passenger_cars) {
    console.warn("Нет разрешения на просмотр транспортных средств.");
    return;
  }

  try {
    const response = await axios.get('/passenger-cars/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    passengerCars.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке легковых автомобилей:', error);
  }
};

const filteredPassengerCars = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return passengerCars.value.filter(car =>
    car.number.toLowerCase().includes(query) ||
    car.brand.toLowerCase().includes(query) ||
    car.model.toLowerCase().includes(query)
  );
});

const openAddModal = () => {
  isAddModalOpen.value = true;
};

const closeAddModal = () => {
  isAddModalOpen.value = false;
};

const addPassengerCar = async () => {
  // Validate all passenger car fields
  const validationErrors = validateFormFields(newPassengerCar.value, fieldDefinitions.passengerCar);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    await axios.post('/passenger-cars/', newPassengerCar.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    newPassengerCar.value = { number: '', brand: '', model: '' };
    fetchPassengerCars();
    closeAddModal();
  } catch (error) {
    console.error('Ошибка при добавлении автомобиля:', error);
    errorModalRef.value?.openModal(error);
  }
};

const openEditModal = (car) => {
  editablePassengerCar.value = { ...car };
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
};

const savePassengerCar = async () => {
  // Validate all passenger car fields
  const validationErrors = validateFormFields(editablePassengerCar.value, fieldDefinitions.passengerCar);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    await axios.put(`/passenger-cars/${editablePassengerCar.value.id}/`, editablePassengerCar.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchPassengerCars();
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных:', error);
    errorModalRef.value?.openModal(error);
  }
};

const deletePassengerCar = async (id) => {
  try {
    await axios.delete(`/passenger-cars/${id}/`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchPassengerCars();
  } catch (error) {
    console.error('Ошибка при удалении автомобиля:', error);
  }
};

const fetchVehicles = async () => {
  if (!permissions.value.view_passenger_cars) {
    console.warn("Нет разрешения на просмотр транспортных средств.");
    return;
  }

  try {
    const response = await axios.get('/vehicles/light-vehicles', {
      headers: { Authorization: `Bearer ${auth.token}` },
    });
    vehicles.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке легковых автомобилей:", error);
  }
};

onMounted(() => {
  console.debug("[DEBUG] Permissions loaded from store:", auth.permissions);
  if (auth.permissions.view_passenger_cars) {
    fetchPassengerCars();
  } else {
    console.warn("[DEBUG] User does not have permission to view passenger cars.");
  }
});
</script>
