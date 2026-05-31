<template>
  <div>
    <!-- Add Modal -->
    <Modal
      :isOpen="showAddModal"
      title="Создать норму ТО"
      @close="closeAddModal"
    >
      <div class="space-y-4">
        <div v-if="addFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ addFormGeneralError }}</p>
        </div>
        <SelectInput
          v-model="form.fire_truck"
          :options="carOptions"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.fire_truck.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.fire_truck.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.fire_truck.required"
          placeholder="Выберите автомобиль"
          :error="addFormErrors.fire_truck"
        />
        <SelectInput
          v-model="form.maintenance_type"
          :options="maintenanceTypeOptions"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.maintenance_type.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.maintenance_type.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.maintenance_type.required"
          placeholder="Выберите вид ТО"
          :error="addFormErrors.maintenance_type"
        />
        <TextInput
          v-model="form.norm"
          type="number"
          step="0.001"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.required"
          placeholder="0.000"
          :error="addFormErrors.norm"
          disallowMinus
          :min="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.minValue"
          :max="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.maxValue"
        />
        <DateInput
          v-model="form.date"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.date.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.date.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.date.required"
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
      title="Редактировать норму ТО"
      @close="closeEditModal"
    >
      <div class="space-y-4">
        <div v-if="editFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ editFormGeneralError }}</p>
        </div>
        <SelectInput
          v-model="form.fire_truck"
          :options="carOptions"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.fire_truck.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.fire_truck.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.fire_truck.required"
          :error="editFormErrors.fire_truck"
        />
        <SelectInput
          v-model="form.maintenance_type"
          :options="maintenanceTypeOptions"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.maintenance_type.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.maintenance_type.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.maintenance_type.required"
          :error="editFormErrors.maintenance_type"
        />
        <TextInput
          v-model="form.norm"
          type="number"
          step="0.001"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.required"
          :error="editFormErrors.norm"
          disallowMinus
          :min="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.minValue"
          :max="fieldDefinitions.normsTechnicalMaintenanceFireTruck.norm.maxValue"
        />
        <DateInput
          v-model="form.date"
          :label="fieldDefinitions.normsTechnicalMaintenanceFireTruck.date.label"
          :hint="fieldDefinitions.normsTechnicalMaintenanceFireTruck.date.hint"
          :required="fieldDefinitions.normsTechnicalMaintenanceFireTruck.date.required"
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
  fire_truck: '',
  maintenance_type: '',
  norm: '',
  date: new Date().toISOString().split('T')[0],
});

const originalAddForm = ref({});
const originalEditForm = ref({});
const editingId = ref(null);

// Maintenance types
const MAINTENANCE_TYPES = [
  { value: 'engine_oil', label: 'Моторное масло' },
  { value: 'air_filter', label: 'Воздушный фильтр' },
  { value: 'cabine_filter', label: 'Салонный фильтр' },
  { value: 'antifreeze', label: 'Антифриз' },
];

const maintenanceTypeOptions = computed(() => MAINTENANCE_TYPES);

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
    fire_truck: '',
    maintenance_type: '',
    norm: '',
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
    fire_truck: norm.fire_truck,
    maintenance_type: norm.maintenance_type,
    norm: norm.norm.toString(),
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
  const validationErrors = validateFormFields(form.value, fieldDefinitions.normsTechnicalMaintenanceFireTruck);
  if (Object.keys(validationErrors).length > 0) {
    addFormErrors.value = validationErrors;
    addFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return; // Don't submit to server
  }

  try {
    const payload = {
      fire_truck: parseInt(form.value.fire_truck),
      maintenance_type: form.value.maintenance_type,
      norm: parseFloat(form.value.norm),
      date: form.value.date,
    };

    const response = await axios.post('technical-maintenance-norms/', payload, {
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
  const validationErrors = validateFormFields(form.value, fieldDefinitions.normsTechnicalMaintenanceFireTruck);
  if (Object.keys(validationErrors).length > 0) {
    editFormErrors.value = validationErrors;
    editFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return; // Don't submit to server
  }

  try {
    const payload = {
      fire_truck: parseInt(form.value.fire_truck),
      maintenance_type: form.value.maintenance_type,
      norm: parseFloat(form.value.norm),
      date: form.value.date,
    };

    const response = await axios.patch(`technical-maintenance-norms/${editingId.value}/`, payload, {
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
