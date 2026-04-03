<template>
  <div>
    <!-- Add Modal -->
    <Modal
      :isOpen="showAddModal"
      title="Создать норму"
      @close="closeAddModal"
    >
      <div class="space-y-4">
        <div v-if="addFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ addFormGeneralError }}</p>
        </div>
        <SelectInput
          v-model="form.car"
          :options="carOptions"
          label="Автомобиль"
          :required="true"
          placeholder="Выберите автомобиль"
          :error="addFormErrors.car"
        />
        <SelectInput
          v-model="form.season"
          :options="[
            { value: 'summer', label: 'Лето' },
            { value: 'winter', label: 'Зима' }
          ]"
          :label="fieldDefinitions.normsPassengerCars.season.label"
          :hint="fieldDefinitions.normsPassengerCars.season.hint"
          :required="fieldDefinitions.normsPassengerCars.season.required"
          :error="addFormErrors.season"
        />
        <TextInput
          v-model="form.city_norm"
          type="number"
          step="0.001"
          :label="fieldDefinitions.normsPassengerCars.city_norm.label"
          :hint="fieldDefinitions.normsPassengerCars.city_norm.hint"
          :required="fieldDefinitions.normsPassengerCars.city_norm.required"
          placeholder="0.000"
          :error="addFormErrors.city_norm"
        />
        <TextInput
          v-model="form.area_norm"
          type="number"
          step="0.001"
          :label="fieldDefinitions.normsPassengerCars.area_norm.label"
          :hint="fieldDefinitions.normsPassengerCars.area_norm.hint"
          :required="fieldDefinitions.normsPassengerCars.area_norm.required"
          placeholder="0.000"
          :error="addFormErrors.area_norm"
        />
        <TextInput
          v-model="form.date"
          type="date"
          :label="fieldDefinitions.normsPassengerCars.date.label"
          :hint="fieldDefinitions.normsPassengerCars.date.hint"
          :required="fieldDefinitions.normsPassengerCars.date.required"
          :error="addFormErrors.date"
        />
      </div>
      <template #footer>
        <Button @click="closeAddModal" variant="secondary">Отмена</Button>
        <Button @click="submitAdd" variant="primary">Создать</Button>
      </template>
    </Modal>

    <!-- Edit Modal -->
    <Modal
      :isOpen="showEditModal"
      title="Редактировать норму"
      @close="closeEditModal"
    >
      <div class="space-y-4">
        <div v-if="editFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ editFormGeneralError }}</p>
        </div>
        <SelectInput
          v-model="form.car"
          :options="carOptions"
          label="Автомобиль"
          :required="true"
          :error="editFormErrors.car"
        />
        <SelectInput
          v-model="form.season"
          :options="[
            { value: 'summer', label: 'Лето' },
            { value: 'winter', label: 'Зима' }
          ]"
          :label="fieldDefinitions.normsPassengerCars.season.label"
          :hint="fieldDefinitions.normsPassengerCars.season.hint"
          :required="fieldDefinitions.normsPassengerCars.season.required"
          :error="editFormErrors.season"
        />
        <TextInput
          v-model="form.city_norm"
          type="number"
          step="0.001"
          :label="fieldDefinitions.normsPassengerCars.city_norm.label"
          :hint="fieldDefinitions.normsPassengerCars.city_norm.hint"
          :required="fieldDefinitions.normsPassengerCars.city_norm.required"
          :error="editFormErrors.city_norm"
        />
        <TextInput
          v-model="form.area_norm"
          type="number"
          step="0.001"
          :label="fieldDefinitions.normsPassengerCars.area_norm.label"
          :hint="fieldDefinitions.normsPassengerCars.area_norm.hint"
          :required="fieldDefinitions.normsPassengerCars.area_norm.required"
          :error="editFormErrors.area_norm"
        />
        <TextInput
          v-model="form.date"
          type="date"
          :label="fieldDefinitions.normsPassengerCars.date.label"
          :hint="fieldDefinitions.normsPassengerCars.date.hint"
          :required="fieldDefinitions.normsPassengerCars.date.required"
          :error="editFormErrors.date"
        />
      </div>
      <template #footer>
        <Button @click="closeEditModal" variant="secondary">Отмена</Button>
        <Button @click="submitEdit" variant="primary">Сохранить</Button>
      </template>
    </Modal>

    <!-- Delete Modal -->
    <Modal
      :isOpen="showDeleteModal"
      title="Подтверждение удаления"
      @close="closeDeleteModal"
    >
      <p>Вы уверены, что хотите удалить {{ deleteCount }} норм(ы)?</p>
      <template #footer>
        <Button @click="closeDeleteModal" variant="secondary">Отмена</Button>
        <Button @click="submitDelete" variant="danger">Удалить</Button>
      </template>
    </Modal>

    <!-- Error Modal -->
    <ErrorModal
      :isOpen="showErrorModal"
      :title="errorModalTitle"
      :message="errorModalMessage"
      @close="showErrorModal = false"
    />

    <!-- Permission Denied Modal -->
    <PermissionDeniedModal
      ref="permissionModal"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, TextInput, SelectInput } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields } from '../utils/errorUtils';
import ErrorModal from './ErrorModal.vue';
import PermissionDeniedModal from './PermissionDeniedModal.vue';

const props = defineProps({
  carOptions: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['add', 'edit', 'delete']);

// Modal states
const showAddModal = ref(false);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const showErrorModal = ref(false);
const errorModalTitle = ref('');
const errorModalMessage = ref('');

// Form data
const form = ref({
  id: null,
  car: null,
  season: 'summer',
  city_norm: '',
  area_norm: '',
  date: ''
});

const deleteCount = ref(0);

// Error handling for add modal
const addFormErrors = ref({
  car: '',
  season: '',
  city_norm: '',
  area_norm: '',
  date: ''
});

const addFormGeneralError = ref('');

// Error handling for edit modal
const editFormErrors = ref({
  car: '',
  season: '',
  city_norm: '',
  area_norm: '',
  date: ''
});

const editFormGeneralError = ref('');

// Field definitions for norms
const normCreateDefinitions = {
  car: {
    label: 'Автомобиль',
    required: true,
    hint: 'Выберите автомобиль'
  },
  ...fieldDefinitions.normsPassengerCars
};
const permissionModal = ref(null);

// Methods
const openAddModal = () => {
  validationError.value = '';
  form.value = {
    id: null,
    car: null,
    season: 'summer',
    city_norm: '',
    area_norm: '',
    date: ''
  };
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  addFormErrors.value = {};
  addFormGeneralError.value = '';
};

const openEditModal = (norm) => {
  editFormErrors.value = {};
  editFormGeneralError.value = '';
  form.value = {
    id: norm.id,
    car: norm.car_id,
    season: norm.season,
    city_norm: norm.city_norm,
    area_norm: norm.area_norm,
    date: norm.date || ''
  };
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editFormErrors.value = {};
  editFormGeneralError.value = '';
};

const openDeleteModal = (count) => {
  deleteCount.value = count;
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const submitAdd = async () => {
  addFormGeneralError.value = '';
  addFormErrors.value = {};

  // Валидация полей на клиенте
  const validationErrors = validateFormFields(form.value, normCreateDefinitions);
  if (Object.keys(validationErrors).length > 0) {
    addFormErrors.value = validationErrors;
    addFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  try {
    await emit('add', {
      car_id: form.value.car,
      season: form.value.season,
      city_norm: parseFloat(form.value.city_norm),
      area_norm: parseFloat(form.value.area_norm),
      date: form.value.date || null
    });
    closeAddModal();
  } catch (error) {
    errorModalTitle.value = 'Ошибка создания норм';
    errorModalMessage.value = error.message || 'Произошла ошибка';
    showErrorModal.value = true;
  }
};

const submitEdit = async () => {
  editFormGeneralError.value = '';
  editFormErrors.value = {};

  // Валидация полей на клиенте
  const validationErrors = validateFormFields(form.value, normCreateDefinitions);
  if (Object.keys(validationErrors).length > 0) {
    editFormErrors.value = validationErrors;
    editFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  try {
    await emit('edit', {
      id: form.value.id,
      car_id: form.value.car,
      season: form.value.season,
      city_norm: parseFloat(form.value.city_norm),
      area_norm: parseFloat(form.value.area_norm),
      date: form.value.date || null
    });
    closeEditModal();
  } catch (error) {
    errorModalTitle.value = 'Ошибка обновления норм';
    errorModalMessage.value = error.message || 'Произошла ошибка';
    showErrorModal.value = true;
  }
};

const submitDelete = () => {
  emit('delete');
  closeDeleteModal();
};

const showError = (title, message) => {
  errorModalTitle.value = title;
  errorModalMessage.value = message;
  showErrorModal.value = true;
};

const showPermissionError = () => {
  permissionModal.value?.openModal();
};

// Expose methods
defineExpose({
  openAddModal,
  openEditModal,
  openDeleteModal,
  showError,
  showPermissionError
});
</script>
