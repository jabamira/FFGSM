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
          :label="fieldDefinitions.normsOperatingHoursFireTruck.car.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.car.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.car.required"
          placeholder="Выберите автомобиль"
          :error="addFormErrors.car"
        />
        <TextInput
          v-model="form.km_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.required"
          placeholder="0.0000"
          :error="addFormErrors.km_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.maxValue"
        />
        <TextInput
          v-model="form.with_pump_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.required"
          placeholder="0.0000"
          :error="addFormErrors.with_pump_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.maxValue"
        />
        <DateInput
          v-model="form.date"
          :label="fieldDefinitions.normsOperatingHoursFireTruck.date.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.date.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.date.required"
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
          :label="fieldDefinitions.normsOperatingHoursFireTruck.car.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.car.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.car.required"
          :error="editFormErrors.car"
        />
        <TextInput
          v-model="form.km_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.required"
          :error="editFormErrors.km_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursFireTruck.km_norm.maxValue"
        />
        <TextInput
          v-model="form.with_pump_norm"
          type="number"
          step="0.0001"
          :label="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.required"
          :error="editFormErrors.with_pump_norm"
          disallowMinus
          :min="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.minValue"
          :max="fieldDefinitions.normsOperatingHoursFireTruck.with_pump_norm.maxValue"
        />
        <DateInput
          v-model="form.date"
          :label="fieldDefinitions.normsOperatingHoursFireTruck.date.label"
          :hint="fieldDefinitions.normsOperatingHoursFireTruck.date.hint"
          :required="fieldDefinitions.normsOperatingHoursFireTruck.date.required"
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
import { Modal, TextInput, SelectInput, Button, DateInput } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields } from '../utils/errorUtils';
import { formatDateToRussian } from '../utils/dateUtils';
import axios from 'axios';

const props = defineProps({
  fireTrucks: {
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
  km_norm: '',
  with_pump_norm: '',
  date: new Date().toISOString().split('T')[0],
});

const originalAddForm = ref({});
const originalEditForm = ref({});
const editingId = ref(null);

const carOptions = computed(() => {
  return props.fireTrucks.map(truck => ({
    value: truck.id,
    label: `${truck.number} - ${truck.brand} ${truck.model}`,
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
    km_norm: '',
    with_pump_norm: '',
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
    km_norm: norm.km_norm.toString(),
    with_pump_norm: norm.with_pump_norm.toString(),
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
  const validationErrors = validateFormFields(form.value, fieldDefinitions.normsOperatingHoursFireTruck);
  if (Object.keys(validationErrors).length > 0) {
    addFormErrors.value = validationErrors;
    addFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return; // Don't submit to server
  }

  try {
    const payload = {
      car: parseInt(form.value.car),
      km_norm: parseFloat(form.value.km_norm),
      with_pump_norm: parseFloat(form.value.with_pump_norm),
      date: form.value.date,
    };

    const response = await axios.post('fire-truck-operating-hours-norms/', payload, {
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
  const validationErrors = validateFormFields(form.value, fieldDefinitions.normsOperatingHoursFireTruck);
  if (Object.keys(validationErrors).length > 0) {
    editFormErrors.value = validationErrors;
    editFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return; // Don't submit to server
  }

  try {
    const payload = {
      car: parseInt(form.value.car),
      km_norm: parseFloat(form.value.km_norm),
      with_pump_norm: parseFloat(form.value.with_pump_norm),
      date: form.value.date,
    };

    const response = await axios.patch(`fire-truck-operating-hours-norms/${editingId.value}/`, payload, {
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
