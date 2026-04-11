<template>
  <Modal
    :is-open="isOpen"
    :title="`Проведение ТО: ${car?.number || truck?.number}`"
    @close="close"
  >
    <div class="space-y-4">
      <!-- Сообщение об ошибке отсутствия нормы -->
      <div v-if="maintenanceInfo?.error" class="rounded-lg p-4 bg-amber-50 border border-amber-200">
        <p class="text-sm font-semibold text-amber-700">⚠️ {{ maintenanceInfo.error }}</p>
      </div>

      <!-- Сводка -->
      <div v-if="!maintenanceInfo?.error" class="bg-gray-50 border border-gray-200 rounded p-4">
        <p class="font-semibold mb-3" :style="{ color: palette.dark }">Сводка</p>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Текущие часы</p>
            <p class="font-semibold" :style="{ color: palette.dark }">{{ (maintenanceInfo?.current_hours || 0).toFixed(2) }} ч</p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Осталось до ТО</p>
            <p class="font-semibold" :style="{ color: maintenanceInfo?.interval !== null && maintenanceInfo?.interval !== undefined && maintenanceInfo.interval < 0 ? '#ef4444' : palette.dark }">
              {{ maintenanceInfo?.interval !== null && maintenanceInfo?.interval !== undefined ? maintenanceInfo.interval.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Интервал между ТО</p>
            <p class="font-semibold" :style="{ color: palette.dark }">
              {{ maintenanceInfo?.norm_interval_value !== null && maintenanceInfo?.norm_interval_value !== undefined ? maintenanceInfo.norm_interval_value.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Следующее ТО</p>
            <p class="font-semibold" :style="{ color: palette.dark }">
              {{ maintenanceInfo?.next_maintenance_at !== null && maintenanceInfo?.next_maintenance_at !== undefined ? maintenanceInfo.next_maintenance_at.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Предыдущее ТО было на</p>
            <p class="font-semibold" :style="{ color: palette.dark }">
              {{ maintenanceInfo?.previous_maintenance_hours !== null && maintenanceInfo?.previous_maintenance_hours !== undefined ? maintenanceInfo.previous_maintenance_hours.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div v-if="maintenanceInfo?.last_maintenance_date">
            <p :style="{ color: palette.medium }" class="text-xs">Дата последнего ТО</p>
            <p class="font-semibold" :style="{ color: palette.dark }">{{ maintenanceInfo?.last_maintenance_date }}</p>
          </div>
        </div>
      </div>

      <!-- Форма проведения ТО -->
      <div v-if="maintenanceInfo && !maintenanceInfo?.error" class="space-y-3">
        <!-- Сообщение об ошибке валидации -->
        <div v-if="Object.keys(formErrors).length > 0" class="rounded-lg p-3 bg-red-50 border border-red-200">
          <p class="text-sm font-semibold text-red-600">{{ error }}</p>
        </div>

        <DateInput 
          v-model="form.date" 
          :label="fieldDefinitions.technicalMaintenance.date.label" 
          :hint="fieldDefinitions.technicalMaintenance.date.hint"
          :error="formErrors.date"
          :required="fieldDefinitions.technicalMaintenance.date.required"
        />
        <TextInput 
          v-model="form.operating_hours" 
          :label="fieldDefinitions.technicalMaintenance.operating_hours.label" 
          :hint="fieldDefinitions.technicalMaintenance.operating_hours.hint"
          :error="formErrors.operating_hours"
          type="number"
          step="0.001"
          placeholder="0.0"
          :required="fieldDefinitions.technicalMaintenance.operating_hours.required"
          min="0"
        />
        <TextInput 
          v-model="form.spent" 
          :label="fieldDefinitions.technicalMaintenance.spent.label" 
          :hint="fieldDefinitions.technicalMaintenance.spent.hint"
          :error="formErrors.spent"
          type="number"
          step="0.1"
          placeholder="0.0"
          min="0"
        />
        <TextInput 
          v-model="form.received" 
          :label="fieldDefinitions.technicalMaintenance.received.label" 
          :hint="fieldDefinitions.technicalMaintenance.received.hint"
          :error="formErrors.received"
          type="number"
          step="0.1"
          placeholder="0.0"
          min="0"
        />
      </div>

      <!-- Сообщение об ошибке -->
      <div v-if="error && Object.keys(formErrors).length === 0" class="rounded-lg p-3 bg-red-50 border border-red-200">
        <p class="text-sm font-semibold text-red-600">{{ error }}</p>
      </div>

      <!-- Статус загрузки -->
      <div v-if="isLoading" class="rounded-lg p-3 bg-yellow-50 border border-yellow-200">
        <p class="text-sm font-semibold text-yellow-700">Проведение ТО...</p>
      </div>
    </div>

    <template #footer>
      <Button variant="secondary" size="md" @click="close" :disabled="isLoading || maintenanceInfo?.error">Отмена</Button>
      <Button variant="primary" size="md" @click="submitMaintenance" :disabled="isLoading || maintenanceInfo?.error">
        {{ isLoading ? 'Сохраняется...' : 'Провести ТО' }}
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Modal, Button, TextInput, DateInput, palette } from './ui/importUi';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields } from '../utils/errorUtils';
import { getNovosibirskDateISO } from '../utils/dateUtils';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  car: {
    type: Object,
    default: null
  },
  truck: {
    type: Object,
    default: null
  },
  maintenanceInfo: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'success']);
const auth = useAuthStore();
const isLoading = ref(false);
const error = ref('');
const formErrors = ref({});
const form = ref({
  date: '',
  operating_hours: '0',
  spent: '0',
  received: '0'
});

const carType = computed(() => {
  return props.car ? 'passenger_car' : 'fire_truck';
});

const carId = computed(() => {
  return props.car?.id || props.truck?.id;
});

// Initialize form when modal opens
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    resetForm();
  }
});

const close = () => {
  resetForm();
  emit('close');
};

const resetForm = () => {
  const today = getNovosibirskDateISO();
  form.value = { 
    date: today,
    operating_hours: '0',
    spent: '0',
    received: '0'
  };
  error.value = '';
  formErrors.value = {};
};

const submitMaintenance = async () => {
  formErrors.value = {};
  error.value = '';

  if (!props.maintenanceInfo) {
    error.value = 'Информация о ТО не загружена';
    return;
  }

  // Подготовить данные для валидации
  const dataToValidate = {
    date: form.value.date,
    operating_hours: form.value.operating_hours,
    spent: form.value.spent,
    received: form.value.received
  };

  // Валидация только полей формы (исключаем car и maintenance_type, которые передаются как props)
  const fieldsToValidate = {
    date: fieldDefinitions.technicalMaintenance.date,
    operating_hours: fieldDefinitions.technicalMaintenance.operating_hours,
    spent: fieldDefinitions.technicalMaintenance.spent,
    received: fieldDefinitions.technicalMaintenance.received
  };

  const validationErrors = validateFormFields(dataToValidate, fieldsToValidate);
  if (Object.keys(validationErrors).length > 0) {
    formErrors.value = validationErrors;
    error.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  isLoading.value = true;

  try {
    const payload = {
      date: form.value.date,
      operating_hours: parseFloat(form.value.operating_hours),
      maintenance_type: props.maintenanceInfo.maintenance_type,
      spent: parseFloat(form.value.spent) || 0,
      received: parseFloat(form.value.received) || 0
    };

    // Определить какой параметр отправлять
    if (props.car) {
      payload.car_id = carId.value;
    } else {
      payload.truck_id = carId.value;
    }

    const response = await axios.post('/technical-maintenance/perform/', payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });

    console.log('[TechnicalMaintenance] ТО проведено успешно:', response.data);
    emit('success');
    close();
  } catch (err) {
    console.error('[TechnicalMaintenance] Ошибка при проведении ТО:', err);
    error.value = err.response?.data?.error || 'Ошибка при проведении ТО';
  } finally {
    isLoading.value = false;
  }
};
</script>
