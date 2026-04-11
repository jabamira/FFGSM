<template>
  <Modal
    :isOpen="showModal"
    title="Редактировать путевой лист"
    @close="closeModal"
  >
    <div class="space-y-4">
      <SelectInput
        v-model="form.car"
        :options="carOptions"
        :label="fieldDefinitions.waybillEdit.car.label"
        :hint="fieldDefinitions.waybillEdit.car.hint"
        :required="fieldDefinitions.waybillEdit.car.required"
        :error="formErrors.car"
      />
      <SelectInput
        v-model="form.driver"
        :options="driverOptions"
        :label="fieldDefinitions.waybillEdit.driver.label"
        :hint="fieldDefinitions.waybillEdit.driver.hint"
        :required="fieldDefinitions.waybillEdit.driver.required"
        :error="formErrors.driver"
      />
      <SelectInput
        v-model="form.norm_season"
        :options="[
          { value: 'summer', label: 'Лето' },
          { value: 'winter', label: 'Зима' }
        ]"
        :label="fieldDefinitions.waybillEdit.norm_season.label"
        :hint="fieldDefinitions.waybillEdit.norm_season.hint"
        :required="fieldDefinitions.waybillEdit.norm_season.required"
        :error="formErrors.norm_season"
      />
      <DateInput
        v-model="form.date"
        :label="fieldDefinitions.waybillEdit.date.label"
        :hint="fieldDefinitions.waybillEdit.date.hint"
        :required="fieldDefinitions.waybillEdit.date.required"
        :error="formErrors.date"
      />
      <div v-if="generalError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
        <p class="text-sm font-semibold text-red-600">{{ generalError }}</p>
      </div>
    </div>
    <template #footer>
      <Button @click="closeModal" variant="secondary">Отмена</Button>
      <Button 
        @click="submitEdit" 
        variant="primary"
        :disabled="isSaveButtonDisabled"
      >
        Сохранить
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, SelectInput, DateInput } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields } from '../utils/errorUtils';
import { getNovosibirskDateISO } from '../utils/dateUtils';

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

const emit = defineEmits(['edit']);

// Modal state
const showModal = ref(false);

// Form data
const form = ref({
  id: null,
  car: null,
  driver: null,
  date: getNovosibirskDateISO(),
  norm_season: 'summer'
});

// Original data for comparison
const originalData = ref({
  id: null,
  car: null,
  driver: null,
  date: getNovosibirskDateISO(),
  norm_season: 'summer'
});

// Error handling
const formErrors = ref({
  car: '',
  driver: '',
  date: '',
  norm_season: ''
});

const generalError = ref('');

// Computed properties
const isSaveButtonDisabled = computed(() => {
  return JSON.stringify(form.value) === JSON.stringify(originalData.value);
});

// Methods
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

const openEditModal = (waybill) => {
  clearErrors();
  form.value = {
    id: waybill.id,
    car: waybill.car,
    driver: waybill.driver,
    date: waybill.date,
    norm_season: waybill.norm_season
  };
  
  // Store original data for comparison
  originalData.value = JSON.parse(JSON.stringify(form.value));
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  clearErrors();
};

const submitEdit = async () => {
  generalError.value = '';
  formErrors.value = {};

  // Валидация полей на клиенте
  const validationErrors = validateFormFields(form.value, fieldDefinitions.waybillEdit);
  if (Object.keys(validationErrors).length > 0) {
    formErrors.value = validationErrors;
    generalError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  try {
    await emit('edit', {
      id: form.value.id,
      car: form.value.car,
      driver: form.value.driver,
      date: form.value.date,
      norm_season: form.value.norm_season
    });
    closeModal();
  } catch (error) {
    generalError.value = error.message || 'Произошла ошибка при сохранении';
  }
};

// Expose methods
defineExpose({
  openEditModal,
  closeModal,
  clearErrors,
  setErrors
});
</script>
