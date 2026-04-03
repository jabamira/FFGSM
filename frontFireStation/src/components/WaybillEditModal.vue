<template>
  <div>
    <!-- Add Modal -->
    <Modal
      :isOpen="showAddModal"
      title="Создать путевой лист"
      @close="closeAddModal"
    >
      <div class="space-y-4">
        <div v-if="generalError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ generalError }}</p>
        </div>
        <SelectInput
          v-model="form.car"
          :options="carOptions"
          :label="fieldDefinitions.waybillCreate.car.label"
          :hint="fieldDefinitions.waybillCreate.car.hint"
          :required="fieldDefinitions.waybillCreate.car.required"
          placeholder="Выберите автомобиль"
          :error="formErrors.car"
        />
        <SelectInput
          v-model="form.driver"
          :options="driverOptions"
          :label="fieldDefinitions.waybillCreate.driver.label"
          :hint="fieldDefinitions.waybillCreate.driver.hint"
          :required="fieldDefinitions.waybillCreate.driver.required"
          placeholder="Выберите водителя"
          :error="formErrors.driver"
        />
        <DateInput
          v-model="form.date"
          :label="fieldDefinitions.waybillCreate.date.label"
          :hint="fieldDefinitions.waybillCreate.date.hint"
          :required="fieldDefinitions.waybillCreate.date.required"
          :error="formErrors.date"
        />
        <SelectInput
          v-model="form.norm_season"
          :options="[
            { value: 'summer', label: 'Лето' },
            { value: 'winter', label: 'Зима' }
          ]"
          :label="fieldDefinitions.waybillCreate.norm_season.label"
          :hint="fieldDefinitions.waybillCreate.norm_season.hint"
          :required="fieldDefinitions.waybillCreate.norm_season.required"
          :error="formErrors.norm_season"
        />
        <SelectInput
          v-model="form.fuel_type"
          :options="fuelTypeOptions"
          :label="fieldDefinitions.waybillCreate.fuel_type.label"
          :hint="fieldDefinitions.waybillCreate.fuel_type.hint"
          :required="fieldDefinitions.waybillCreate.fuel_type.required"
          :error="formErrors.fuel_type"
        />
      </div>
      <template #footer>
        <Button @click="closeAddModal" variant="secondary">Отмена</Button>
        <Button @click="submitAdd" variant="primary">Создать</Button>
      </template>
    </Modal>

    <!-- Delete Modal -->
    <Modal
      :isOpen="showDeleteModal"
      title="Подтверждение удаления"
      @close="closeDeleteModal"
    >
      <p>Вы уверены, что хотите удалить {{ deleteCount }} путевой(ые) лист(ы)?</p>
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
import { Modal, Button, TextInput, SelectInput, DateInput } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import ErrorModal from './ErrorModal.vue';
import PermissionDeniedModal from './PermissionDeniedModal.vue';
import { fuelTypeOptions } from '../config/fuelTypes';
import { validateFormFields } from '../utils/errorUtils';

const props = defineProps({
  carOptions: {
    type: Array,
    required: true
  },
  driverOptions: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['add', 'edit', 'delete']);

// Modal states
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showErrorModal = ref(false);
const errorModalTitle = ref('');
const errorModalMessage = ref('');

// Form data
const form = ref({
  id: null,
  car: null,
  driver: null,
  date: new Date().toISOString().split('T')[0],
  norm_season: 'summer',
  fuel_type: 'petrol95'
});

const validationError = ref('');
const deleteCount = ref(0);
const permissionModal = ref(null);

// Error handling
const formErrors = ref({
  car: '',
  driver: '',
  date: '',
  norm_season: '',
  fuel_type: ''
});

const generalError = ref('');

// Methods
const getCurrentSeason = () => {
  const month = new Date().getMonth() + 1;
  return (month >= 5 && month <= 9) ? 'summer' : 'winter';
};

const clearErrors = () => {
  Object.keys(formErrors.value).forEach(key => {
    formErrors.value[key] = '';
  });
  generalError.value = '';
};

const setErrors = (errors, message = '') => {
  clearErrors();
  if (typeof errors === 'object') {
    Object.keys(errors).forEach(key => {
      if (formErrors.value.hasOwnProperty(key)) {
        formErrors.value[key] = errors[key];
      }
    });
  }
  if (message) {
    generalError.value = message;
  }
};

const openAddModal = () => {
  clearErrors();
  form.value = {
    id: null,
    car: null,
    driver: null,
    date: new Date().toISOString().split('T')[0],
    norm_season: getCurrentSeason(),
    fuel_type: 'petrol95'
  };
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  clearErrors();
};

const openDeleteModal = (count) => {
  deleteCount.value = count;
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const submitAdd = async () => {
  generalError.value = '';
  formErrors.value = {};

  // Валидация полей на клиенте
  const validationErrors = validateFormFields(form.value, fieldDefinitions.waybillCreate);
  if (Object.keys(validationErrors).length > 0) {
    formErrors.value = validationErrors;
    generalError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  emit('add', {
    car: form.value.car,
    driver: form.value.driver,
    date: form.value.date,
    norm_season: form.value.norm_season,
    fuel_type: form.value.fuel_type
  });
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
  openDeleteModal,
  showError,
  showPermissionError,
  clearErrors,
  setErrors
});
</script>
