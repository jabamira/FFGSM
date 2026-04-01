<template>
  <!-- Odometer Modal -->
  <Modal
    :is-open="isOpen"
    :title="title"
    @close="handleClose"
  >
    <div class="space-y-4">
      <div v-if="isRequired" class="bg-blue-50 border border-blue-200 rounded p-3">
        <p style="color: #1e40af">
          ⚠️ Внесение стартовых данных обязательно для дальнейших расчетов.
          Пожалуйста, заполните эту информацию сейчас.
        </p>
      </div>
      <div class="min-w-96 space-y-4">
        <TextInput 
          v-model.number="form.odometer" 
          label="Показания одометра (км)"
          placeholder="Введите показания одометра"
          type="number"
          :required="true"
        />
        <TextInput 
          v-model.number="form.fuel" 
          label="Остаток топлива (л)"
          placeholder="Введите остаток топлива"
          type="number"
          step="0.001"
          :required="true"
        />
        <DateInput 
          v-model="form.date" 
          label="Дата"
          :required="true"
        />
      </div>
    </div>
    <template #footer>
      <Button 
        v-if="!isRequired"
        variant="secondary" 
        size="md" 
        @click="handleClose"
      >
        Отмена
      </Button>
      <Button 
        v-if="isRequired"
        variant="secondary" 
        size="md" 
        @click="showWarning = true"
      >
        Отмена
      </Button>
      <Button variant="primary" size="md" @click="submitData">
        Сохранить
      </Button>
    </template>
  </Modal>

  <!-- Warning Modal for Required Odometer -->
  <Modal
    :is-open="showWarning"
    title="Подтверждение"
    @close="showWarning = false"
  >
    <div class="space-y-4">
      <p style="color: #dc2626">
        Внесение стартовых данных обязательно для корректных расчетов расхода топлива.
        Вы уверены, что хотите пропустить этот шаг?
      </p>
    </div>
    <template #footer>
      <Button variant="secondary" size="md" @click="showWarning = false">
        Вернуться и заполнить
      </Button>
      <Button variant="danger" size="md" @click="skipOdometer">
        Пропустить
      </Button>
    </template>
  </Modal>
  <PermissionDeniedModal ref="permissionDeniedModal" />
  <ErrorModal ref="errorModalRef" />
</template>

<script setup>
import { ref, watch } from 'vue';
import { Modal, Button, TextInput, DateInput } from './ui/importUi';
import PermissionDeniedModal from './PermissionDeniedModal.vue';
import ErrorModal from './ErrorModal.vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { validateFormFields } from '../utils/errorUtils';
import { fieldDefinitions } from '../config/fieldDefinitions';

const auth = useAuthStore();
const permissionDeniedModal = ref(null);
const errorModalRef = ref(null);

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  carId: {
    type: Number,
    default: null
  },
  carType: {
    type: String,
    enum: ['fire-truck', 'passenger-car'],
    required: true
  },
  isRequired: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Внесение стартовых данных'
  }
});

const emit = defineEmits(['close', 'submitted', 'skipped']);

const getCurrentLocalDate = () => {
  const now = new Date();
  // Новосибирск UTC+7 - добавляем 7 часов к UTC
  const novosibirskTime = new Date(now.getTime() + 7 * 60 * 60 * 1000);
  return novosibirskTime.toISOString().split('T')[0];
};

const form = ref({
  odometer: '',
  fuel: '',
  date: getCurrentLocalDate()
});

const showWarning = ref(false);

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    form.value = {
      odometer: '',
      fuel: '',
      date: getCurrentLocalDate()
    };
    showWarning.value = false;
  }
});

const getEndpoint = () => {
  return props.carType === 'fire-truck' 
    ? '/fire-truck-odometer-fuel/'
    : '/passenger-car-odometer-fuel/';
};

const handleClose = () => {
  if (props.isRequired) {
    showWarning.value = true;
  } else {
    emit('close');
  }
};

const skipOdometer = () => {
  showWarning.value = false;
  emit('skipped');
};

const submitData = async () => {
  try {
    // Валидация данных перед отправкой
    const validationData = {
      odometer: form.value.odometer,
      fuel: form.value.fuel,
      date: form.value.date
    };

    const errors = validateFormFields(validationData, fieldDefinitions.odometerFuel);
    if (Object.keys(errors).length > 0) {
      // Создаем объект ошибки в формате, который понимает ErrorModal
      const errorObj = {
        response: {
          data: {}
        }
      };
      
      Object.entries(errors).forEach(([field, message]) => {
        errorObj.response.data[field] = message;
      });
      
      errorModalRef.value?.openModal(errorObj);
      return;
    }

    // Проверка разрешения в зависимости от типа машины
    const isFireTruck = props.carType === 'fire-truck';
    const requiredPermission = isFireTruck 
      ? 'can_create_fire_trucks'
      : 'can_create_passenger_cars';

    if (!auth.permissions[requiredPermission]) {
      permissionDeniedModal.value?.openModal(requiredPermission);
      return;
    }

    const payload = {
      car: props.carId,
      odometer: parseInt(form.value.odometer),
      fuel: parseFloat(form.value.fuel),
      date: form.value.date
    };

    await axios.post(getEndpoint(), payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });

    console.log(`[OdometerModal] Odometer data saved successfully`);
    emit('submitted');
  } catch (error) {
    console.error('[OdometerModal] Error saving odometer data:', error);
    
    // Показать ошибку в модальном окне вместо выброса
    errorModalRef.value?.openModal(error);
  }
};
</script>
