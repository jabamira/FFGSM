<template>
  <div>
    <!-- Add Modal -->
    <Modal
      :isOpen="showAddModal"
      title="Создать коэффициент моточасов"
      @close="closeAddModal"
    >
      <div class="space-y-4">
        <div v-if="addFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ addFormGeneralError }}</p>
        </div>
        <SelectInput
          v-model="form.car"
          :options="carOptions"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.car.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.car.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.car.required"
          placeholder="Выберите автомобиль"
          :error="addFormErrors.car"
        />
        <TextInput
          v-model="form.city_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.required"
          placeholder="0.0000"
          :error="addFormErrors.city_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.maxValue"
        />
        <TextInput
          v-model="form.area_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.required"
          placeholder="0.0000"
          :error="addFormErrors.area_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.maxValue"
        />
        <TextInput
          v-model="form.date"
          type="date"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.date.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.date.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.date.required"
          :error="addFormErrors.date"
        />
      </div>
      <template #footer>
        <Button @click="closeAddModal" variant="secondary">Отмена</Button>
        <Button @click="submitAdd" variant="primary" :disabled="!isAddFormChanged">Создать</Button>
      </template>
    </Modal>

    <!-- Edit Modal -->
    <Modal
      :isOpen="showEditModal"
      title="Редактировать коэффициент моточасов"
      @close="closeEditModal"
    >
      <div class="space-y-4">
        <div v-if="editFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ editFormGeneralError }}</p>
        </div>
        <SelectInput
          v-model="form.car"
          :options="carOptions"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.car.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.car.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.car.required"
          :error="editFormErrors.car"
        />
        <TextInput
          v-model="form.city_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.required"
          :error="editFormErrors.city_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursPassengerCar.city_norm.maxValue"
        />
        <TextInput
          v-model="form.area_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.required"
          :error="editFormErrors.area_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursPassengerCar.area_norm.maxValue"
        />
        <TextInput
          v-model="form.date"
          type="date"
          :label="fieldDefinitions.normsOperatingHoursPassengerCar.date.label"
          :hint="fieldDefinitions.normsOperatingHoursPassengerCar.date.hint"
          :required="fieldDefinitions.normsOperatingHoursPassengerCar.date.required"
          :error="editFormErrors.date"
        />
      </div>
      <template #footer>
        <Button @click="closeEditModal" variant="secondary">Отмена</Button>
        <Button @click="submitEdit" variant="primary" :disabled="!isEditFormChanged">Сохранить</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, TextInput, SelectInput, Button } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields } from '../utils/errorUtils';
import { formatDateToRussian } from '../utils/dateUtils';
import axios from 'axios';

const props = defineProps({
  passengerCars: {
    type: Array,
    default: () => [],
  },
  auth: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['norm-added', 'norm-updated', 'error']);

// State
const showAddModal = ref(false);
const showEditModal = ref(false);
const addFormGeneralError = ref('');
const editFormGeneralError = ref('');
const addFormErrors = ref({});
const editFormErrors = ref({});

const form = ref({
  car: '',
  city_norm: '',
  area_norm: '',
  date: new Date().toISOString().split('T')[0],
});

const originalAddForm = ref({});
const originalEditForm = ref({});
const editingId = ref(null);

const carOptions = computed(() => {
  return props.passengerCars.map(car => ({
    value: car.id,
    label: `${car.number} - ${car.brand} ${car.model}`,
  }));
});

const isAddFormChanged = computed(() => {
  return JSON.stringify(form.value) !== JSON.stringify(originalAddForm.value);
});

const isEditFormChanged = computed(() => {
  return JSON.stringify(form.value) !== JSON.stringify(originalEditForm.value);
});

// Methods
const openAddModal = () => {
  form.value = {
    car: '',
    city_norm: '',
    area_norm: '',
    date: new Date().toISOString().split('T')[0],
  };
  originalAddForm.value = JSON.parse(JSON.stringify(form.value));
  addFormErrors.value = {};
  addFormGeneralError.value = '';
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
};

const openEditModal = (norm) => {
  editingId.value = norm.id;
  form.value = {
    car: norm.car,
    city_norm: norm.city_norm.toString(),
    area_norm: norm.area_norm.toString(),
    date: norm.date,
  };
  originalEditForm.value = JSON.parse(JSON.stringify(form.value));
  editFormErrors.value = {};
  editFormGeneralError.value = '';
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingId.value = null;
};

const parseErrors = (errorData) => {
  const errors = {};
  if (Array.isArray(errorData)) {
    if (errorData.length > 0) {
      const firstError = errorData[0];
      if (typeof firstError === 'string') {
        return { general: firstError };
      }
      if (firstError.non_field_errors) {
        return { general: firstError.non_field_errors[0] };
      }
      Object.keys(firstError).forEach(key => {
        if (Array.isArray(firstError[key])) {
          errors[key] = firstError[key][0];
        } else {
          errors[key] = firstError[key];
        }
      });
    }
  } else if (typeof errorData === 'object') {
    if (errorData.non_field_errors) {
      return { general: errorData.non_field_errors[0] };
    }
    Object.keys(errorData).forEach(key => {
      if (Array.isArray(errorData[key])) {
        errors[key] = errorData[key][0];
      } else {
        errors[key] = errorData[key];
      }
    });
  }
  return errors;
};

const submitAdd = async () => {
  addFormErrors.value = {};
  addFormGeneralError.value = '';

  // CLIENT-SIDE VALIDATION
  const validationErrors = validateFormFields(form.value, fieldDefinitions.normsOperatingHoursPassengerCar);
  if (Object.keys(validationErrors).length > 0) {
    addFormErrors.value = validationErrors;
    addFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return; // Don't submit to server
  }

  try {
    const payload = {
      car: parseInt(form.value.car),
      city_norm: parseFloat(form.value.city_norm),
      area_norm: parseFloat(form.value.area_norm),
      date: form.value.date,
    };

    const response = await axios.post('passenger-car-operating-hours-norms/', payload, {
      headers: { Authorization: `Bearer ${props.auth.access}` },
    });

    emit('norm-added', response.data);
    closeAddModal();
  } catch (error) {
    const errorData = error.response?.data;
    const parsedErrors = parseErrors(errorData);

    if (parsedErrors.general) {
      addFormGeneralError.value = parsedErrors.general;
      delete parsedErrors.general;
    }
    addFormErrors.value = parsedErrors;
    emit('error', error);
  }
};

const submitEdit = async () => {
  editFormErrors.value = {};
  editFormGeneralError.value = '';

  // CLIENT-SIDE VALIDATION
  const validationErrors = validateFormFields(form.value, fieldDefinitions.normsOperatingHoursPassengerCar);
  if (Object.keys(validationErrors).length > 0) {
    editFormErrors.value = validationErrors;
    editFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return; // Don't submit to server
  }

  try {
    const payload = {
      car: parseInt(form.value.car),
      city_norm: parseFloat(form.value.city_norm),
      area_norm: parseFloat(form.value.area_norm),
      date: form.value.date,
    };

    const response = await axios.patch(`passenger-car-operating-hours-norms/${editingId.value}/`, payload, {
      headers: { Authorization: `Bearer ${props.auth.access}` },
    });

    emit('norm-updated', response.data);
    closeEditModal();
  } catch (error) {
    const errorData = error.response?.data;
    const parsedErrors = parseErrors(errorData);

    if (parsedErrors.general) {
      editFormGeneralError.value = parsedErrors.general;
      delete parsedErrors.general;
    }
    editFormErrors.value = parsedErrors;
    emit('error', error);
  }
};

defineExpose({
  openAddModal,
  openEditModal,
  closeAddModal,
  closeEditModal,
});
</script>
