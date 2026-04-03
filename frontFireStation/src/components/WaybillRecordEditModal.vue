<template>
  <div>
    <!-- Add/Edit Record Modal -->
    <Modal
      :isOpen="showModal"
      :title="isEditMode ? 'Редактировать запись' : 'Добавить запись'"
      @close="closeModal"
    >
      <div class="space-y-4">
        <div v-if="generalError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ generalError }}</p>
        </div>
        <TextInput
          v-model="form.target"
          :label="fieldDefinitions.waybillRecord.target.label"
          :hint="fieldDefinitions.waybillRecord.target.hint"
          placeholder="Введите цель выезда"
          :required="fieldDefinitions.waybillRecord.target.required"
          :error="formErrors.target"
        />

        <div class="time-input-full-width">
          <TimeInput
            v-model="form.departure_time"
            :label="fieldDefinitions.waybillRecord.departure_time.label"
            :hint="fieldDefinitions.waybillRecord.departure_time.hint"
            :required="fieldDefinitions.waybillRecord.departure_time.required"
            :error="formErrors.departure_time"
          />
        </div>

        <div class="time-input-full-width">
          <TimeInput
            v-model="form.arrival_time"
            :label="fieldDefinitions.waybillRecord.arrival_time.label"
            :hint="fieldDefinitions.waybillRecord.arrival_time.hint"
            :required="fieldDefinitions.waybillRecord.arrival_time.required"
            :error="formErrors.arrival_time"
          />
        </div>

        <TextInput
          v-model.number="form.distance_city_km"
          :label="fieldDefinitions.waybillRecord.distance_city_km.label"
          :hint="fieldDefinitions.waybillRecord.distance_city_km.hint"
          type="number"
          placeholder="0"
          min="0"
          :required="fieldDefinitions.waybillRecord.distance_city_km.required"
          :error="formErrors.distance_city_km"
        />

        <TextInput
          v-model.number="form.distance_area_km"
          :label="fieldDefinitions.waybillRecord.distance_area_km.label"
          :hint="fieldDefinitions.waybillRecord.distance_area_km.hint"
          type="number"
          placeholder="0"
          min="0"
          :required="fieldDefinitions.waybillRecord.distance_area_km.required"
          :error="formErrors.distance_area_km"
        />

        <TextInput
          v-model.number="form.fuel_refueled"
          :label="fieldDefinitions.waybillRecord.fuel_refueled.label"
          :hint="fieldDefinitions.waybillRecord.fuel_refueled.hint"
          type="number"
          placeholder="0"
          step="0.001"
          min="0"
          :required="fieldDefinitions.waybillRecord.fuel_refueled.required"
          :error="formErrors.fuel_refueled"
        />

        <TextInput
          v-model.number="form.fuel_used"
          :label="fieldDefinitions.waybillRecord.fuel_used.label"
          :hint="fieldDefinitions.waybillRecord.fuel_used.hint"
          type="number"
          placeholder="0"
          step="0.001"
          min="0"
          :required="fieldDefinitions.waybillRecord.fuel_used.required"
          :error="formErrors.fuel_used"
        />

        <!-- Fire Truck specific fields -->
        <TextInput
          v-if="isFireTruck"
          v-model.number="form.odometer_after"
          :label="fieldDefinitions.waybillRecord.odometer_after.label"
          :hint="fieldDefinitions.waybillRecord.odometer_after.hint"
          type="number"
          placeholder="0"
          min="0"
          :required="fieldDefinitions.waybillRecord.odometer_after.required"
          :error="formErrors.odometer_after"
        />

        <TextInput
          v-if="isFireTruck"
          v-model.number="form.time_with_pump"
          :label="fieldDefinitions.waybillRecord.time_with_pump.label"
          :hint="fieldDefinitions.waybillRecord.time_with_pump.hint"
          type="number"
          placeholder="0"
          min="0"
          :required="fieldDefinitions.waybillRecord.time_with_pump.required"
          :error="formErrors.time_with_pump"
        />

        <TextInput
          v-if="isFireTruck"
          v-model.number="form.time_without_pump"
          :label="fieldDefinitions.waybillRecord.time_without_pump.label"
          :hint="fieldDefinitions.waybillRecord.time_without_pump.hint"
          type="number"
          placeholder="0"
          min="0"
          :required="fieldDefinitions.waybillRecord.time_without_pump.required"
          :error="formErrors.time_without_pump"
        />

        
      </div>

      <template #footer>
        <Button @click="closeModal" variant="secondary">Отмена</Button>
        <Button @click="submitForm" variant="primary">
          {{ isEditMode ? 'Сохранить' : 'Добавить' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, TextInput, TimeInput } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields } from '../utils/errorUtils';

const emit = defineEmits(['add', 'edit']);
const props = defineProps({
  isFireTruck: {
    type: Boolean,
    default: false
  }
});

// Modal state
const showModal = ref(false);
const isEditMode = ref(false);

// Form data
const form = ref({
  id: null,
  target: '',
  departure_time: '',
  arrival_time: '',
  distance_city_km: 0,
  distance_area_km: 0,
  fuel_refueled: 0,
  fuel_used: 0,
  odometer_after: 0,
  time_with_pump: 0,
  time_without_pump: 0
});

// Original data for comparison (edit mode)
const originalData = ref(null);

// Errors
const formErrors = ref({
  target: '',
  departure_time: '',
  arrival_time: '',
  distance_city_km: '',
  distance_area_km: '',
  fuel_refueled: '',
  fuel_used: '',
  odometer_after: '',
  time_with_pump: '',
  time_without_pump: ''
});

const generalError = ref('');

// Field definitions for validation (combine with isFireTruck-specific fields)
const getValidationDefinitions = () => {
  const base = {
    target: fieldDefinitions.waybillRecord.target,
    departure_time: fieldDefinitions.waybillRecord.departure_time,
    arrival_time: fieldDefinitions.waybillRecord.arrival_time,
    distance_city_km: fieldDefinitions.waybillRecord.distance_city_km,
    distance_area_km: fieldDefinitions.waybillRecord.distance_area_km,
    fuel_refueled: fieldDefinitions.waybillRecord.fuel_refueled,
    fuel_used: fieldDefinitions.waybillRecord.fuel_used
  };

  if (props.isFireTruck) {
    base.odometer_after = fieldDefinitions.waybillRecord.odometer_after;
    base.time_with_pump = fieldDefinitions.waybillRecord.time_with_pump;
    base.time_without_pump = fieldDefinitions.waybillRecord.time_without_pump;
  }

  return base;
};

// Methods
const clearErrors = () => {
  Object.keys(formErrors.value).forEach(key => {
    formErrors.value[key] = '';
  });
  generalError.value = '';
};

// Получить текущее время в формате HH:MM
const getCurrentTime = () => {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
};

const openAddModal = () => {
  isEditMode.value = false;
  originalData.value = null;
  clearErrors();
  const currentTime = getCurrentTime();
  form.value = {
    id: null,
    target: '',
    departure_time: currentTime,
    arrival_time: currentTime,
    distance_city_km: 0,
    distance_area_km: 0,
    fuel_refueled: 0,
    fuel_used: 0,
    odometer_after: 0,
    time_with_pump: 0,
    time_without_pump: 0
  };
  showModal.value = true;
};

const openEditModal = (record) => {
  isEditMode.value = true;
  clearErrors();
  form.value = {
    id: record.id,
    target: record.target || '',
    departure_time: record.departure_time || '',
    arrival_time: record.arrival_time || '',
    distance_city_km: record.distance_city_km || 0,
    distance_area_km: record.distance_area_km || 0,
    fuel_refueled: record.fuel_refueled || 0,
    fuel_used: record.fuel_used || 0,
    odometer_after: record.odometer_after || 0,
    time_with_pump: record.time_with_pump || 0,
    time_without_pump: record.time_without_pump || 0
  };
  originalData.value = JSON.parse(JSON.stringify(form.value));
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  clearErrors();
};

const submitForm = async () => {
  clearErrors();

  // Валидация полей на клиенте
  const validationErrors = validateFormFields(form.value, getValidationDefinitions());
  if (Object.keys(validationErrors).length > 0) {
    formErrors.value = validationErrors;
    generalError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  // Нормализовать время
  const normalizeTime = (timeStr) => {
    if (!timeStr || typeof timeStr !== 'string') return '';
    const trimmed = timeStr.trim();
    if (!trimmed) return '';
    const parts = trimmed.split(':');
    if (parts.length >= 2) {
      const hours = String(parseInt(parts[0] || 0)).padStart(2, '0');
      const minutes = String(parseInt(parts[1] || 0)).padStart(2, '0');
      return `${hours}:${minutes}`;
    }
    return trimmed;
  };

  const departure_time = normalizeTime(form.value.departure_time);
  const arrival_time = normalizeTime(form.value.arrival_time);
  const fuel_refueled = form.value.fuel_refueled !== null && form.value.fuel_refueled !== '' 
    ? parseFloat(form.value.fuel_refueled) 
    : 0;
  const fuel_used = form.value.fuel_used !== null && form.value.fuel_used !== '' 
    ? parseFloat(form.value.fuel_used) 
    : 0;
  
  const baseData = {
    target: form.value.target,
    departure_time: departure_time,
    arrival_time: arrival_time,
    distance_city_km: form.value.distance_city_km,
    distance_area_km: form.value.distance_area_km,
    fuel_refueled: fuel_refueled,
    fuel_used: fuel_used
  };

  // Add fire truck specific fields if applicable
  if (props.isFireTruck) {
    baseData.odometer_after = form.value.odometer_after;
    baseData.time_with_pump = form.value.time_with_pump;
    baseData.time_without_pump = form.value.time_without_pump;
  }
  
  if (isEditMode.value) {
    emit('edit', {
      id: form.value.id,
      ...baseData
    });
  } else {
    emit('add', baseData);
  }
  closeModal();
};

// Expose methods
defineExpose({
  openAddModal,
  openEditModal,
  closeModal
});
</script>

<style scoped>
.time-input-full-width {
  display: flex;
  flex-direction: column;
}

.time-input-full-width :deep(input) {
  width: 100%;
}
</style>
