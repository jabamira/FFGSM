<template>
  <Modal
    :is-open="isOpen"
    :title="`Проведение ТО: ${car?.number || truck?.number}`"
    @close="close"
  >
    <div class="space-y-4">
      <!-- Выбор вида ТО (если доступны несколько видов) -->
      <div v-if="allMaintenanceItems && allMaintenanceItems.length > 0" class="space-y-2">
        <label :style="{ color: palette.dark }" class="block text-sm font-medium">Вид ТО</label>
        <div class="space-y-2 max-h-48 overflow-y-auto border border-gray-200 rounded p-2">
          <button
            v-for="item in allMaintenanceItems"
            :key="item.maintenance_type"
            @click="selectMaintenanceType(item)"
            :style="{
              backgroundColor: getMaintenanceColor(item.interval),
              color: '#fff',
              padding: '8px 12px',
              borderRadius: '4px',
              border: form.maintenance_type === item.maintenance_type ? '2px solid white' : 'none',
              fontWeight: form.maintenance_type === item.maintenance_type ? 'bold' : 'normal',
              cursor: 'pointer'
            }"
            class="w-full text-left hover:shadow transition-shadow"
          >
            {{ getMaintenanceTypeLabel(item.maintenance_type) }}: {{ item.interval.toFixed(2) }} ч
          </button>
        </div>
      </div>

      <!-- Сообщение об ошибке отсутствия нормы -->
      <div v-if="allMaintenanceInfo?.error" class="rounded-lg p-4 bg-amber-50 border border-amber-200">
        <p class="text-sm font-semibold text-amber-700">⚠️ {{ allMaintenanceInfo.error }}</p>
      </div>

      <!-- Сводка -->
      <div v-if="currentMaintenanceInfo && !allMaintenanceInfo?.error" class="bg-gray-50 border border-gray-200 rounded p-4">
        <p class="font-semibold mb-3" :style="{ color: palette.dark }">Сводка: {{ getMaintenanceTypeLabel(currentMaintenanceInfo.maintenance_type) }}</p>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Текущие часы</p>
            <p class="font-semibold" :style="{ color: palette.dark }">{{ (allMaintenanceInfo?.current_hours || 0).toFixed(2) }} ч</p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Осталось до ТО</p>
            <p class="font-semibold" :style="{ color: currentMaintenanceInfo?.interval !== null && currentMaintenanceInfo?.interval !== undefined && currentMaintenanceInfo.interval < 0 ? '#ef4444' : palette.dark }">
              {{ currentMaintenanceInfo?.interval !== null && currentMaintenanceInfo?.interval !== undefined ? currentMaintenanceInfo.interval.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Интервал между ТО</p>
            <p class="font-semibold" :style="{ color: palette.dark }">
              {{ currentMaintenanceInfo?.norm_interval_value !== null && currentMaintenanceInfo?.norm_interval_value !== undefined ? currentMaintenanceInfo.norm_interval_value.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Следующее ТО</p>
            <p class="font-semibold" :style="{ color: palette.dark }">
              {{ currentMaintenanceInfo?.next_maintenance_at !== null && currentMaintenanceInfo?.next_maintenance_at !== undefined ? currentMaintenanceInfo.next_maintenance_at.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div>
            <p :style="{ color: palette.medium }" class="text-xs">Предыдущее ТО было на</p>
            <p class="font-semibold" :style="{ color: palette.dark }">
              {{ currentMaintenanceInfo?.previous_maintenance_hours !== null && currentMaintenanceInfo?.previous_maintenance_hours !== undefined ? currentMaintenanceInfo.previous_maintenance_hours.toFixed(2) : 'N/A' }} ч
            </p>
          </div>
          <div v-if="currentMaintenanceInfo?.last_maintenance_date">
            <p :style="{ color: palette.medium }" class="text-xs">Дата последнего ТО</p>
            <p class="font-semibold" :style="{ color: palette.dark }">{{ currentMaintenanceInfo?.last_maintenance_date }}</p>
          </div>
        </div>
      </div>

      <!-- Форма проведения ТО -->
      <div v-if="currentMaintenanceInfo && !allMaintenanceInfo?.error" class="space-y-3">
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
      <Button variant="secondary" size="md" @click="close" :disabled="isLoading || allMaintenanceInfo?.error">Отмена</Button>
      <Button variant="primary" size="md" @click="submitMaintenance" :disabled="isLoading || allMaintenanceInfo?.error || !currentMaintenanceInfo">
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
  spent: '0',
  received: '0',
  maintenance_type: ''
});

const carType = computed(() => {
  return props.car ? 'passenger_car' : 'fire_truck';
});

const carId = computed(() => {
  return props.car?.id || props.truck?.id;
});

// Маппинг для переводов видов ТО
const maintenanceTypeLabels = {
  'engine_oil': 'Замена моторного масла и фильтра',
  'air_filter': 'Замена воздушного фильтра',
  'cabine_filter': 'Замена салонного фильтра',
  'antifreeze': 'Замена антифриза'
};

const getMaintenanceTypeLabel = (typeCode) => {
  return maintenanceTypeLabels[typeCode] || typeCode;
};

// Получить все варианты ТО для этой машины
const allMaintenanceInfo = computed(() => {
  return props.car?.all_maintenance_info || props.truck?.all_maintenance_info || { items: [], error: null };
});

const allMaintenanceItems = computed(() => {
  return allMaintenanceInfo.value?.items || [];
});

// Текущая информация о выбранном виде ТО
const currentMaintenanceInfo = ref(null);

const getMaintenanceColor = (interval) => {
  if (interval < 0) return '#ef4444';  // Красный - просрочено
  if (interval < 10) return '#ef4444';  // Красный - менее 10 часов
  if (interval < 50) return '#f97316';  // Оранжевый  - 10-50 часов
  return '#10b981';  // Зелёный - 50+ часов
};

const selectMaintenanceType = (item) => {
  form.value.maintenance_type = item.maintenance_type;
  // Обновить сводку для выбранного вида ТО
  currentMaintenanceInfo.value = item;
};

// Watch для автоматического обновления selectedMaintenanceInfo в родительском компоненте
watch(() => form.value.maintenance_type, (newType) => {
  if (newType) {
    const selectedItem = allMaintenanceItems.value.find(item => item.maintenance_type === newType);
    if (selectedItem) {
      currentMaintenanceInfo.value = selectedItem;
    }
  }
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
  // Установить maintenance_type на первый доступный или пустой
  const firstType = allMaintenanceItems.value.length > 0 ? allMaintenanceItems.value[0].maintenance_type : '';
  const firstItem = allMaintenanceItems.value.length > 0 ? allMaintenanceItems.value[0] : null;
  
  form.value = { 
    date: today,
    spent: '0',
    received: '0',
    maintenance_type: firstType
  };
  currentMaintenanceInfo.value = firstItem;
  error.value = '';
  formErrors.value = {};
};

const submitMaintenance = async () => {
  formErrors.value = {};
  error.value = '';

  if (!currentMaintenanceInfo.value) {
    error.value = 'Информация о ТО не загружена';
    return;
  }

  // Подготовить данные для валидации
  const dataToValidate = {
    date: form.value.date,
    spent: form.value.spent,
    received: form.value.received
  };

  // Валидация только полей формы (исключаем car и maintenance_type, которые передаются как props)
  const fieldsToValidate = {
    date: fieldDefinitions.technicalMaintenance.date,
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
      maintenance_type: form.value.maintenance_type,
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
