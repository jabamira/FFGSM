<template>
  <div>
    <!-- Add/Edit Record Modal -->
    <Modal
      :isOpen="showModal"
      :title="isEditMode ? 'Редактировать запись' : 'Добавить запись'"
      @close="closeModal"
    >
      <div class="space-y-4">
        <TextInput
          v-model="form.target"
          label="Цель выезда"
          placeholder="Введите цель выезда"
          :required="true"
          :error="errors.target"
        />

        <div class="time-input-full-width">
          <TimeInput
            v-model="form.departure_time"
            label="Выезд"
            :required="true"
            :error="errors.departure_time"
          />
        </div>

        <div class="time-input-full-width">
          <TimeInput
            v-model="form.arrival_time"
            label="Прибытие"
            :required="true"
            :error="errors.arrival_time"
          />
        </div>

        <TextInput
          v-model.number="form.distance_city_km"
          label="Км по городу"
          type="number"
          placeholder="0"
          min="0"
          :required="true"
          :error="errors.distance_city_km"
        />

        <TextInput
          v-model.number="form.distance_area_km"
          label="Км по области"
          type="number"
          placeholder="0"
          min="0"
          :required="true"
          :error="errors.distance_area_km"
        />

        <TextInput
          v-model.number="form.fuel_refueled"
          label="Заправлено (л)"
          type="number"
          placeholder="0"
          step="0.1"
          min="0"
          :error="errors.fuel_refueled"
        />

        <TextInput
          v-model.number="form.fuel_used"
          label="Израсходовано (л)"
          type="number"
          placeholder="0"
          step="0.1"          min="0"          :required="true"
          :error="errors.fuel_used"
        />

        <div v-if="generalError" class="text-sm text-red-600 bg-red-50 p-3 rounded">
          {{ generalError }}
        </div>
      </div>

      <template #footer>
        <Button @click="closeModal" variant="secondary">Отмена</Button>
        <Button 
          @click="submitForm" 
          variant="primary"
          :disabled="!isFormValid"
        >
          {{ isEditMode ? 'Сохранить' : 'Добавить' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, TextInput, TimeInput } from './ui/importUi';

const emit = defineEmits(['add', 'edit']);

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
  fuel_used: 0
});

// Original data for comparison (edit mode)
const originalData = ref(null);

// Errors
const errors = ref({
  target: '',
  departure_time: '',
  arrival_time: '',
  distance_city_km: '',
  distance_area_km: '',
  fuel_refueled: '',
  fuel_used: ''
});

const generalError = ref('');

// Computed properties
const isFormValid = computed(() => {
  // In edit mode: form must differ from original
  if (isEditMode.value) {
    return !areFormAndOriginalEqual();
  }
  
  // In add mode: enable if ANY field has content (excluding fuel_refueled which is optional)
  const hasAnyContent = 
    form.value.target.trim() !== '' ||
    form.value.departure_time.trim() !== '' ||
    form.value.arrival_time.trim() !== '' ||
    (form.value.distance_city_km !== null && form.value.distance_city_km !== '') ||
    (form.value.distance_area_km !== null && form.value.distance_area_km !== '') ||
    (form.value.fuel_used !== null && form.value.fuel_used !== '');
  
  return hasAnyContent;
});

const areFormAndOriginalEqual = () => {
  if (!originalData.value) return false;
  return JSON.stringify(form.value) === JSON.stringify(originalData.value);
};

// Methods
const validateTime = (timeStr) => {
  // HTML5 time input format is already validated by the browser
  // We just need to check if it's not empty
  return timeStr.trim() !== '';
};

const clearErrors = () => {
  Object.keys(errors.value).forEach(key => {
    errors.value[key] = '';
  });
  generalError.value = '';
};

const validateForm = () => {
  clearErrors();
  let isValid = true;

  // Validate target (only if provided)
  if (form.value.target.trim() && form.value.target.trim().length < 2) {
    errors.value.target = 'Цель выезда должна быть не менее 2 символов';
    isValid = false;
  }

  // Validate departure_time (only if provided)
  if (form.value.departure_time.trim() && !validateTime(form.value.departure_time)) {
    errors.value.departure_time = 'Некорректное время выезда';
    isValid = false;
  }

  // Validate arrival_time (only if provided)
  if (form.value.arrival_time.trim() && !validateTime(form.value.arrival_time)) {
    errors.value.arrival_time = 'Некорректное время прибытия';
    isValid = false;
  }

  // Validate distance_city_km (only if provided)
  if (form.value.distance_city_km !== null && form.value.distance_city_km !== '') {
    if (form.value.distance_city_km < 0) {
      errors.value.distance_city_km = 'Значение не может быть отрицательным';
      isValid = false;
    }
  }

  // Validate distance_area_km (only if provided)
  if (form.value.distance_area_km !== null && form.value.distance_area_km !== '') {
    if (form.value.distance_area_km < 0) {
      errors.value.distance_area_km = 'Значение не может быть отрицательным';
      isValid = false;
    }
  }

  // Validate fuel_refueled (only if provided)
  if (form.value.fuel_refueled && form.value.fuel_refueled !== 0) {
    if (form.value.fuel_refueled < 0) {
      errors.value.fuel_refueled = 'Значение не может быть отрицательным';
      isValid = false;
    }
  }

  // Validate fuel_used (only if provided)
  if (form.value.fuel_used !== null && form.value.fuel_used !== '') {
    if (form.value.fuel_used < 0) {
      errors.value.fuel_used = 'Значение не может быть отрицательным';
      isValid = false;
    }
  }

  return isValid;
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
    fuel_used: 0
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
    fuel_used: record.fuel_used || 0
  };
  originalData.value = JSON.parse(JSON.stringify(form.value));
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  clearErrors();
};

// Нормализовать время в формат HH:MM
const normalizeTime = (timeStr) => {
  if (!timeStr || typeof timeStr !== 'string') return '';
  
  // Убедиться что время не пустая строка
  const trimmed = timeStr.trim();
  if (!trimmed) return '';
  
  // Если время в формате HH:MM:SS или HH:MM, извлечь HH:MM
  const parts = trimmed.split(':');
  if (parts.length >= 2) {
    const hours = String(parseInt(parts[0] || 0)).padStart(2, '0');
    const minutes = String(parseInt(parts[1] || 0)).padStart(2, '0');
    return `${hours}:${minutes}`;
  }
  
  return trimmed;
};

// Преобразовать топливо в число (default 0)
const normalizeFuelRefueled = (value) => {
  // Если значение null, undefined или пустая строка - вернуть 0
  if (value === null || value === undefined || value === '') {
    return 0;
  }
  
  const num = parseFloat(value);
  // Если NaN, вернуть 0
  if (isNaN(num)) {
    return 0;
  }
  
  // Вернуть число
  return num;
};

const submitForm = async () => {
  if (!validateForm()) {
    generalError.value = 'Пожалуйста исправьте ошибки в форме';
    return;
  }

  try {
    const departure_time = normalizeTime(form.value.departure_time);
    const arrival_time = normalizeTime(form.value.arrival_time);
    const fuel_refueled = normalizeFuelRefueled(form.value.fuel_refueled);
    const fuel_used = form.value.fuel_used !== null && form.value.fuel_used !== '' 
      ? parseFloat(form.value.fuel_used) 
      : 0;
    
    if (isEditMode.value) {
      await emit('edit', {
        id: form.value.id,
        target: form.value.target,
        departure_time: departure_time,
        arrival_time: arrival_time,
        distance_city_km: form.value.distance_city_km,
        distance_area_km: form.value.distance_area_km,
        fuel_refueled: fuel_refueled,
        fuel_used: fuel_used
      });
    } else {
      await emit('add', {
        target: form.value.target,
        departure_time: departure_time,
        arrival_time: arrival_time,
        distance_city_km: form.value.distance_city_km,
        distance_area_km: form.value.distance_area_km,
        fuel_refueled: fuel_refueled,
        fuel_used: fuel_used
      });
    }
    closeModal();
  } catch (error) {
    generalError.value = error.message || 'Ошибка при сохранении записи';
  }
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
