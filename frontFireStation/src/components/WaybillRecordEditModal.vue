<template>
  <div>
    <!-- Add/Edit Record Modal -->
    <Modal
      :isOpen="showModal"
      :title="isEditMode ? 'Редактировать запись' : 'Добавить запись'"
      @close="closeModal"
    >
      <div class="space-y-4" ref="formContainer">
        <div v-if="generalError" role="alert" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600 whitespace-pre-line">{{ generalError }}</p>
        </div>
        <TextInput
          v-model="form.target"
          :label="fieldDefinitions.waybillRecord.target.label"
          :hint="fieldDefinitions.waybillRecord.target.hint"
          placeholder="Введите цель выезда"
          :required="fieldDefinitions.waybillRecord.target.required"
          :error="formErrors.target"
          :data-error="formErrors.target ? 'target' : null"
        />

        <div class="time-input-full-width">
          <TimeInput
            v-model="form.departure_time"
            :label="fieldDefinitions.waybillRecord.departure_time.label"
            :hint="fieldDefinitions.waybillRecord.departure_time.hint"
            :required="fieldDefinitions.waybillRecord.departure_time.required"
            :error="formErrors.departure_time"
            :data-error="formErrors.departure_time ? 'departure_time' : null"
          />
        </div>

        <div class="time-input-full-width">
          <TimeInput
            v-model="form.arrival_time"
            :label="fieldDefinitions.waybillRecord.arrival_time.label"
            :hint="fieldDefinitions.waybillRecord.arrival_time.hint"
            :required="fieldDefinitions.waybillRecord.arrival_time.required"
            :error="formErrors.arrival_time"
            :data-error="formErrors.arrival_time ? 'arrival_time' : null"
          />
        </div>

        <TextInput
          v-model.number="form.distance_city_km"
          :positiveIntegerOnly="true"
          @change="validateNumberField('distance_city_km')"
          :label="fieldDefinitions.waybillRecord.distance_city_km.label"
          :hint="fieldDefinitions.waybillRecord.distance_city_km.hint"
          placeholder="0"
          :required="fieldDefinitions.waybillRecord.distance_city_km.required"
          :error="formErrors.distance_city_km"
          :data-error="formErrors.distance_city_km ? 'distance_city_km' : null"
        />

        <TextInput
          v-model.number="form.distance_area_km"
          :positiveIntegerOnly="true"
          @change="validateNumberField('distance_area_km')"
          :label="fieldDefinitions.waybillRecord.distance_area_km.label"
          :hint="fieldDefinitions.waybillRecord.distance_area_km.hint"
          placeholder="0"
          :required="fieldDefinitions.waybillRecord.distance_area_km.required"
          :error="formErrors.distance_area_km"
          :data-error="formErrors.distance_area_km ? 'distance_area_km' : null"
        />

        <TextInput
          v-model.number="form.fuel_refueled"
          :disallowMinus="true"
          @change="validateNumberField('fuel_refueled')"
          :label="fieldDefinitions.waybillRecord.fuel_refueled.label"
          :hint="fieldDefinitions.waybillRecord.fuel_refueled.hint"
          type="number"
          placeholder="0"
          step="0.001"
          min="0"
          :required="fieldDefinitions.waybillRecord.fuel_refueled.required"
          :error="formErrors.fuel_refueled"
          :data-error="formErrors.fuel_refueled ? 'fuel_refueled' : null"
        />

        <TextInput
          v-model.number="form.fuel_used"
          :disallowMinus="true"
          @change="validateNumberField('fuel_used')"
          :label="fieldDefinitions.waybillRecord.fuel_used.label"
          :hint="fieldDefinitions.waybillRecord.fuel_used.hint"
          type="number"
          placeholder="0"
          step="0.001"
          min="0"
          :required="fieldDefinitions.waybillRecord.fuel_used.required"
          :error="formErrors.fuel_used"
          :data-error="formErrors.fuel_used ? 'fuel_used' : null"
        />

        <!-- Fire Truck specific fields -->
        <TextInput
          v-if="isFireTruck"
          v-model.number="form.odometer_after"
          :positiveIntegerOnly="true"
          @change="validateNumberField('odometer_after')"
          :label="fieldDefinitions.waybillRecord.odometer_after.label"
          :hint="fieldDefinitions.waybillRecord.odometer_after.hint"
          placeholder="0"
          :required="fieldDefinitions.waybillRecord.odometer_after.required"
          :error="formErrors.odometer_after"
          :data-error="formErrors.odometer_after ? 'odometer_after' : null"
        />

        <TextInput
          v-if="isFireTruck"
          v-model.number="form.time_with_pump"
          :positiveIntegerOnly="true"
          @change="validateNumberField('time_with_pump')"
          :label="fieldDefinitions.waybillRecord.time_with_pump.label"
          :hint="fieldDefinitions.waybillRecord.time_with_pump.hint"
          placeholder="0"
          :required="fieldDefinitions.waybillRecord.time_with_pump.required"
          :error="formErrors.time_with_pump"
          :data-error="formErrors.time_with_pump ? 'time_with_pump' : null"
        />

        <TextInput
          v-if="isFireTruck"
          v-model.number="form.time_without_pump"
          :positiveIntegerOnly="true"
          @change="validateNumberField('time_without_pump')"
          :label="fieldDefinitions.waybillRecord.time_without_pump.label"
          :hint="fieldDefinitions.waybillRecord.time_without_pump.hint"
          placeholder="0"
          :required="fieldDefinitions.waybillRecord.time_without_pump.required"
          :error="formErrors.time_without_pump"
          :data-error="formErrors.time_without_pump ? 'time_without_pump' : null"
        />

        
      </div>

      <template #footer>
        <Button @click="closeModal" variant="secondary">Отмена</Button>
        <Button @click="submitForm" variant="primary" :disabled="!canSave">
          {{ isEditMode ? 'Сохранить' : 'Добавить' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue';
import { Modal, Button, TextInput, TimeInput } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields, validateSingleField } from '../utils/errorUtils';

const emit = defineEmits(['add', 'edit']);
const props = defineProps({
  isFireTruck: {
    type: Boolean,
    default: false
  }
});

// Refs
const formContainer = ref(null);

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

// Check if form has changed
const formHasChanged = computed(() => {
  if (!originalData.value) return false;
  
  const currentForm = form.value;
  
  return (
    currentForm.target !== originalData.value.target ||
    currentForm.departure_time !== originalData.value.departure_time ||
    currentForm.arrival_time !== originalData.value.arrival_time ||
    currentForm.distance_city_km !== originalData.value.distance_city_km ||
    currentForm.distance_area_km !== originalData.value.distance_area_km ||
    currentForm.fuel_refueled !== originalData.value.fuel_refueled ||
    currentForm.fuel_used !== originalData.value.fuel_used ||
    (props.isFireTruck && (
      currentForm.odometer_after !== originalData.value.odometer_after ||
      currentForm.time_with_pump !== originalData.value.time_with_pump ||
      currentForm.time_without_pump !== originalData.value.time_without_pump
    ))
  );
});

// Check if save button should be enabled
const canSave = computed(() => {
  if (isEditMode.value) {
    return formHasChanged.value;
  }
  // For add mode, always allow save
  return true;
});

// Methods
const clearErrors = () => {
  Object.keys(formErrors.value).forEach(key => {
    formErrors.value[key] = '';
  });
  generalError.value = '';
};

// Validate numeric field format in real-time
const validateNumberField = (fieldName) => {
  const value = form.value[fieldName];
  const fieldDef = getValidationDefinitions()[fieldName];
  
  if (!fieldDef) return;
  
  const error = validateSingleField(fieldName, value, fieldDef);
  if (error) {
    formErrors.value[fieldName] = error;
  } else {
    formErrors.value[fieldName] = '';
  }
  
  // Очистить общую ошибку валидации при изменении одометра
  if (fieldName === 'odometer_after' && generalError.value) {
    generalError.value = '';
  }
};

// Метод для отображения ошибки валидации от сервера внутри модали
const setValidationError = (errorMessage, fieldName = null) => {
  // Попытаемся улучшить сообщение об ошибке одометра
  let displayError = errorMessage;
  
  // Если это ошибка одометра - распарсим и переформатируем сообщение
  if (errorMessage.includes('одометр') && errorMessage.includes('не может быть меньше')) {
    const match = errorMessage.match(/одометр после поездки \((\d+)\).*?одометр перед поездкой \((\d+)\)/);
    if (match) {
      const inputValue = match[1];
      const dbValue = match[2];
      displayError = `Ошибка: Одометр после поездки\n\nВы ввели: ${inputValue} км\nТекущее значение в БД: ${dbValue} км\n\nЗначение одометра может только увеличиваться. Пожалуйста, введите значение больше чем ${dbValue}.`;
    }
  }
  
  generalError.value = displayError;
  
  // Прокрутить форму вверх чтобы увидеть ошибку
  nextTick(() => {
    // Сначала попробуем найти элемент ошибки
    const errorElement = formContainer.value?.querySelector('[role="alert"]') 
      || formContainer.value?.querySelector('.bg-red-50');
    
    if (errorElement) {
      console.log('[setValidationError] Скроллим к элементу ошибки');
      errorElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    
    // Если fieldName указан, пытаемся найти поле с ошибкой
    if (fieldName && formContainer.value) {
      const fieldElement = formContainer.value.querySelector(`[data-error="${fieldName}"]`)
        || formContainer.value.querySelector(`input[data-testid="${fieldName}"]`)
        || formContainer.value.querySelector(`[name="${fieldName}"]`);
      
      if (fieldElement) {
        console.log(`[setValidationError] Скроллим к полю ${fieldName}`);
        fieldElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }
    
    // По умолчанию скроллим к верху контейнера
    if (formContainer.value) {
      console.log('[setValidationError] Скроллим к верху формы');
      formContainer.value.scrollTop = 0;
    }
  });
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
  console.log('[WaybillRecordEditModal] openEditModal called with record:', {
    id: record.id,
    target: record.target,
    departure_time: record.departure_time,
    arrival_time: record.arrival_time,
    distance_city_km: record.distance_city_km,
    distance_area_km: record.distance_area_km,
    fuel_refueled: record.fuel_refueled,
    fuel_used: record.fuel_used,
    odometer_after: record.odometer_after,
    time_with_pump: record.time_with_pump,
    time_without_pump: record.time_without_pump
  });
  
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
  
  console.log('[WaybillRecordEditModal] form.value after assignment:', form.value);
  
  originalData.value = JSON.parse(JSON.stringify(form.value));
  showModal.value = true;
  
  console.log('[WaybillRecordEditModal] Modal opened, showModal =', showModal.value);
};

const closeModal = () => {
  showModal.value = false;
  clearErrors();
};

const scrollToTop = async () => {
  await nextTick();
  
  console.log('[WaybillRecordEditModal] scrollToTop called');
  
  if (formContainer.value) {
    console.log('[WaybillRecordEditModal] formContainer exists');
    
    // Способ 1: Ищем ближайший элемент с overflow
    let scrollableParent = formContainer.value.closest('.overflow-y-auto');
    
    if (scrollableParent) {
      console.log('[WaybillRecordEditModal] Found scrollable parent, scrolling to 0');
      scrollableParent.scrollTop = 0;
    } else {
      console.log('[WaybillRecordEditModal] No scrollable parent found');
      
      // Способ 2: Скролим сам formContainer в видимость
      formContainer.value.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Способ 3: Также найдем первое поле с ошибкой и скролим его в видимость
    const errorField = formContainer.value.querySelector('[data-error]');
    if (errorField) {
      console.log('[WaybillRecordEditModal] Found error field, scrolling into view');
      errorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  } else {
    console.warn('[WaybillRecordEditModal] formContainer ref is not available');
  }
};

const submitForm = async () => {
  clearErrors();

  // Нормализовать время в формат HH:MM
  const normalizeTime = (timeStr) => {
    if (!timeStr || typeof timeStr !== 'string') return '';
    const trimmed = timeStr.trim();
    if (!trimmed) return '';
    
    // Если уже в формате HH:MM, вернуть как есть
    if (/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(trimmed)) {
      return trimmed;
    }
    
    // Извлечь только цифры
    const digits = trimmed.replace(/\D/g, '');
    
    // Если есть ровно 4 цифры (HHMM)
    if (digits.length === 4) {
      const hours = String(parseInt(digits.slice(0, 2))).padStart(2, '0');
      const minutes = String(parseInt(digits.slice(2, 4))).padStart(2, '0');
      
      // Проверить валидность
      const h = parseInt(hours);
      const m = parseInt(minutes);
      if (h >= 0 && h < 24 && m >= 0 && m < 60) {
        return `${hours}:${minutes}`;
      }
    }
    
    // Попытаться распарсить строку с двоеточием
    if (trimmed.includes(':')) {
      const parts = trimmed.split(':');
      if (parts.length >= 2) {
        const h = parseInt(parts[0] || 0);
        const m = parseInt(parts[1] || 0);
        
        if (h >= 0 && h < 24 && m >= 0 && m < 60) {
          const hours = String(h).padStart(2, '0');
          const minutes = String(m).padStart(2, '0');
          return `${hours}:${minutes}`;
        }
      }
    }
    
    return trimmed;
  };

  // Форматировать decimal число с 3 знаками после запятой
  const formatDecimal = (value) => {
    if (value === null || value === '' || isNaN(value)) return 0;
    const num = parseFloat(value);
    return parseFloat(num.toFixed(3));
  };

  // Валидация полей на клиенте
  const departure_time = normalizeTime(form.value.departure_time);
  const arrival_time = normalizeTime(form.value.arrival_time);
  
  // Обновить форму с нормализованными временами перед валидацией
  form.value.departure_time = departure_time;
  form.value.arrival_time = arrival_time;
  
  const validationErrors = validateFormFields(form.value, getValidationDefinitions());
  if (Object.keys(validationErrors).length > 0) {
    console.warn('[WaybillRecordEditModal] Validation errors:', validationErrors);
    formErrors.value = validationErrors;
    generalError.value = 'Пожалуйста, проверьте заполненные поля';
    await scrollToTop();
    return;
  }

  const fuel_refueled = formatDecimal(form.value.fuel_refueled);
  const fuel_used = formatDecimal(form.value.fuel_used);
  
  console.log('[WaybillRecordEditModal] Formatted fuel values for submission:', {
    fuel_refueled_raw: form.value.fuel_refueled,
    fuel_refueled_formatted: fuel_refueled,
    fuel_used_raw: form.value.fuel_used,
    fuel_used_formatted: fuel_used
  });
  
  const baseData = {
    target: form.value.target,
    departure_time: departure_time,
    arrival_time: arrival_time,
    distance_city_km: parseInt(form.value.distance_city_km) || 0,
    distance_area_km: parseInt(form.value.distance_area_km) || 0,
    fuel_refueled: fuel_refueled,
    fuel_used: fuel_used
  };

  // Add fire truck specific fields if applicable
  if (props.isFireTruck) {
    baseData.odometer_after = parseInt(form.value.odometer_after) || 0;
    baseData.time_with_pump = parseInt(form.value.time_with_pump) || 0;
    baseData.time_without_pump = parseInt(form.value.time_without_pump) || 0;
  }
  
  console.log('[WaybillRecordEditModal] Submitting record data:', {
    isEditMode: isEditMode.value,
    baseData,
    isFireTruck: props.isFireTruck,
    validation: {
      fuel_refueled_valid: fuel_refueled >= 0 && fuel_refueled <= 999.999,
      fuel_used_valid: fuel_used >= 0 && fuel_used <= 999.999,
      distance_city_km_valid: form.value.distance_city_km >= 0 && form.value.distance_city_km <= 999999,
      distance_area_km_valid: form.value.distance_area_km >= 0 && form.value.distance_area_km <= 999999,
      odometer_after_valid: !props.isFireTruck || (form.value.odometer_after >= 0 && form.value.odometer_after <= 999999),
      time_with_pump_valid: !props.isFireTruck || (form.value.time_with_pump >= 0 && form.value.time_with_pump <= 999999),
      time_without_pump_valid: !props.isFireTruck || (form.value.time_without_pump >= 0 && form.value.time_without_pump <= 999999)
    }
  });
  
  if (isEditMode.value) {
    emit('edit', {
      id: form.value.id,
      ...baseData
    });
  } else {
    emit('add', baseData);
  }
  // НЕ закрываем модаль здесь! Она закроется после успешного сохранения в родителе
  // closeModal() будет вызвана из handleAddRecord/handleEditRecord в WaybillManagement.vue
};

// Expose methods
defineExpose({
  openAddModal,
  openEditModal,
  closeModal,
  setValidationError
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

/* Ensure form container scrolls on overflow */
:deep(.modal-content) {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
