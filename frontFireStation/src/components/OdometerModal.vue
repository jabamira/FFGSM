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
        <TextInput 
          v-model="form.date" 
          label="Дата"
          type="date"
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
</template>

<script setup>
import { ref, watch } from 'vue';
import { Modal, Button, TextInput } from './ui/importUi';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();

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

const form = ref({
  odometer: '',
  fuel: '',
  date: new Date().toISOString().split('T')[0]
});

const showWarning = ref(false);

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    form.value = {
      odometer: '',
      fuel: '',
      date: new Date().toISOString().split('T')[0]
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
    throw error;
  }
};
</script>
