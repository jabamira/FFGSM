<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Список пожарных автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <template v-if="permissions.can_create_fire_trucks">
          <Button label="Добавить автомобиль" variant="primary" @click="openAddModal" class="mb-4" />
        </template>
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите данные для поиска" class="mb-4" />
        <DataTable :data="filteredFireTrucks" :columns="columns" @row-click="permissions.can_update_fire_trucks ? openEditModal : null">
          <template #actions="{ row }">
            <Button v-if="permissions.can_delete_fire_trucks" label="Удалить" variant="danger" @click="deleteFireTruck(row.id)" />
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Error Modal -->
    <ErrorModal ref="errorModalRef" />

    <!-- Permission Denied Modal -->
    <PermissionDeniedModal ref="permissionDeniedModal" />

    <!-- Add Fire Truck Modal -->
    <Modal :is-open="isAddModalOpen" title="Добавить автомобиль" @close="closeAddModal">
      <div class="space-y-4 min-w-96">
        <TextInput 
          v-model="newFireTruck.number" 
          :label="fieldDefinitions.fireTruck.number.label" 
          :hint="fieldDefinitions.fireTruck.number.hint"
          placeholder="Гос. номер"
          :required="fieldDefinitions.fireTruck.number.required"
        />
        <TextInput 
          v-model="newFireTruck.brand" 
          :label="fieldDefinitions.fireTruck.brand.label" 
          :hint="fieldDefinitions.fireTruck.brand.hint"
          placeholder="Марка"
          :required="fieldDefinitions.fireTruck.brand.required"
        />
        <TextInput 
          v-model="newFireTruck.model" 
          :label="fieldDefinitions.fireTruck.model.label" 
          :hint="fieldDefinitions.fireTruck.model.hint"
          placeholder="Модель"
          :required="fieldDefinitions.fireTruck.model.required"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeAddModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="addFireTruck">Добавить</Button>
      </template>
    </Modal>

    <!-- Edit Fire Truck Modal -->
    <Modal :is-open="isEditModalOpen" title="Редактировать данные" @close="closeEditModal">
      <div class="space-y-4 min-w-96">
        <TextInput 
          v-model="editableFireTruck.number" 
          :label="fieldDefinitions.fireTruck.number.label" 
          :hint="fieldDefinitions.fireTruck.number.hint"
          placeholder="Гос. номер"
          :required="fieldDefinitions.fireTruck.number.required"
        />
        <TextInput 
          v-model="editableFireTruck.brand" 
          :label="fieldDefinitions.fireTruck.brand.label" 
          :hint="fieldDefinitions.fireTruck.brand.hint"
          placeholder="Марка"
          :required="fieldDefinitions.fireTruck.brand.required"
        />
        <TextInput 
          v-model="editableFireTruck.model" 
          :label="fieldDefinitions.fireTruck.model.label" 
          :hint="fieldDefinitions.fireTruck.model.hint"
          placeholder="Модель"
          :required="fieldDefinitions.fireTruck.model.required"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeEditModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="saveFireTruck">Сохранить</Button>
      </template>
    </Modal>
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
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';

const auth = useAuthStore();
const fireTrucks = ref([]);
const searchQuery = ref('');
const errorModalRef = ref(null);
const permissionDeniedModal = ref(null);
const isAddModalOpen = ref(false);
const isEditModalOpen = ref(false);
const newFireTruck = ref({ number: '', brand: '', model: '' });
const editableFireTruck = ref({});
const permissions = computed(() => auth.permissions);

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' },
  { key: 'actions', label: 'Действия', slot: true }
];

const fetchFireTrucks = async () => {
  if (!permissions.value.view_fire_trucks) {
    console.warn("Нет разрешения на просмотр транспортных средств.");
    return;
  }

  try {
    const response = await axios.get('/fire-trucks', {
      headers: { Authorization: `Bearer ${auth.access}` },
    });
    fireTrucks.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке пожарных автомобилей:", error);
    errorModalRef.value?.openModal(error);
  }
};

const filteredFireTrucks = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return fireTrucks.value.filter(truck =>
    truck.number.toLowerCase().includes(query) ||
    truck.brand.toLowerCase().includes(query) ||
    truck.model.toLowerCase().includes(query)
  );
});

const openAddModal = () => {
  isAddModalOpen.value = true;
};

const closeAddModal = () => {
  isAddModalOpen.value = false;
};

const addFireTruck = async () => {
  // Validate all fire truck fields
  const validationErrors = validateFormFields(newFireTruck.value, fieldDefinitions.fireTruck);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    await axios.post('/fire-trucks/', newFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fetchFireTrucks();
    closeAddModal();
  } catch (error) {
    console.error('Ошибка при добавлении автомобиля:', error);
    errorModalRef.value?.openModal(error);
  }
};

const openEditModal = (truck) => {
  editableFireTruck.value = { ...truck };
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
};

const saveFireTruck = async () => {
  // Validate all fire truck fields
  const validationErrors = validateFormFields(editableFireTruck.value, fieldDefinitions.fireTruck);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    await axios.put(`/fire-trucks/${editableFireTruck.value.id}/`, editableFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fetchFireTrucks();
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных:', error);
    errorModalRef.value?.openModal(error);
  }
};

const deleteFireTruck = async (id) => {
  if (!permissions.value.can_delete_fire_trucks) {
    permissionDeniedModal.value?.openModal('can_delete_fire_trucks');
    return;
  }

  try {
    await axios.delete(`/fire-trucks/${id}/`, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fetchFireTrucks();
  } catch (error) {
    console.error('Ошибка при удалении автомобиля:', error);
    errorModalRef.value?.openModal(error);
  }
};

onMounted(() => {
  console.debug("[DEBUG] Permissions loaded from store:", auth.permissions);
  if (auth.permissions.view_fire_trucks) {
    fetchFireTrucks();
  } else {
    console.warn("[DEBUG] User does not have permission to view fire trucks.");
  }
});
</script>
