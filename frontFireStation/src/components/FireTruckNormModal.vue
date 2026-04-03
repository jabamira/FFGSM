<template>
  <Modal
    :isOpen="isOpen"
    title="Добавить норму расхода топлива"
    @close="handleClose"
  >
    <div class="space-y-4">
      <!-- Error Message -->
      <div v-if="errorMessage" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
        <p class="text-sm font-semibold text-red-600">{{ errorMessage }}</p>
      </div>

      <!-- Info Message -->
      <div class="rounded-lg p-4 bg-blue-50 border-l-4 border-blue-500">
        <p class="text-sm text-blue-900">
          <span class="font-semibold">Машина:</span> {{ carNumber }} | 
          <span class="font-semibold">Сезон:</span> {{ seasonDisplay }}
        </p>
      </div>

      <!-- Form Fields -->
      <TextInput
        v-model.number="form.with_pump_norm"
        :label="fieldDefinitions.normsFireTrucks.with_pump_norm.label"
        :hint="fieldDefinitions.normsFireTrucks.with_pump_norm.hint"
        type="number"
        placeholder="0.000"
        step="0.001"
        min="0"
        :required="fieldDefinitions.normsFireTrucks.with_pump_norm.required"
        :error="errors.with_pump_norm"
      />

      <TextInput
        v-model.number="form.without_pump_norm"
        :label="fieldDefinitions.normsFireTrucks.without_pump_norm.label"
        :hint="fieldDefinitions.normsFireTrucks.without_pump_norm.hint"
        type="number"
        placeholder="0.000"
        step="0.001"
        min="0"
        :required="fieldDefinitions.normsFireTrucks.without_pump_norm.required"
        :error="errors.without_pump_norm"
      />

      <TextInput
        v-model.number="form.km_norm"
        :label="fieldDefinitions.normsFireTrucks.km_norm.label"
        :hint="fieldDefinitions.normsFireTrucks.km_norm.hint"
        type="number"
        placeholder="0.000"
        step="0.001"
        min="0"
        :required="fieldDefinitions.normsFireTrucks.km_norm.required"
        :error="errors.km_norm"
      />

      <DateInput
        v-model="form.date"
        :label="fieldDefinitions.normsFireTrucks.date.label"
        :hint="fieldDefinitions.normsFireTrucks.date.hint"
        :required="fieldDefinitions.normsFireTrucks.date.required"
        :error="errors.date"
      />
    </div>

    <template #footer>
      <Button variant="secondary" size="md" @click="handleClose">Отмена</Button>
      <Button 
        variant="primary" 
        size="md" 
        @click="submitForm"
        :disabled="isSaving"
      >
        {{ isSaving ? 'Сохранение...' : 'Добавить норму' }}
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, TextInput, DateInput } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields } from '../utils/errorUtils';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const emit = defineEmits(['close', 'success']);
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  carId: {
    type: Number,
    default: null
  },
  carNumber: {
    type: String,
    default: ''
  },
  season: {
    type: String,
    default: 'winter'
  }
});

const auth = useAuthStore();

// Form data
const form = ref({
  with_pump_norm: '',
  without_pump_norm: '',
  km_norm: '',
  date: new Date().toISOString().split('T')[0]
});

// Errors
const errors = ref({
  with_pump_norm: '',
  without_pump_norm: '',
  km_norm: '',
  date: ''
});

const errorMessage = ref('');
const isSaving = ref(false);

const seasonDisplay = computed(() => {
  return props.season === 'summer' ? 'Лето' : 'Зима';
});

const clearErrors = () => {
  Object.keys(errors.value).forEach(key => {
    errors.value[key] = '';
  });
  errorMessage.value = '';
};

const validateForm = () => {
  const validationErrors = validateFormFields(form.value, fieldDefinitions.normsFireTrucks);
  clearErrors();
  if (Object.keys(validationErrors).length > 0) {
    Object.assign(errors.value, validationErrors);
    return false;
  }
  return true;
};

const submitForm = async () => {
  if (!validateForm()) {
    errorMessage.value = 'Пожалуйста заполните все обязательные поля';
    return;
  }

  if (!props.carId) {
    errorMessage.value = 'Ошибка: не найден ID машины';
    return;
  }

  isSaving.value = true;
  try {
    const payload = {
      car: props.carId,
      season: props.season,
      with_pump_norm: parseFloat(form.value.with_pump_norm),
      without_pump_norm: parseFloat(form.value.without_pump_norm),
      km_norm: parseFloat(form.value.km_norm),
      date: form.value.date
    };

    await axios.post('fire-truck-norms/', payload, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });

    console.log('[FireTruckNormModal] Norm created successfully');
    emit('success');
    handleClose();
  } catch (error) {
    console.error('Error creating norm:', error);
    errorMessage.value = error.response?.data?.detail || 
                        error.response?.data?.non_field_errors?.[0] ||
                        'Ошибка при сохранении нормы';
  } finally {
    isSaving.value = false;
  }
};

const handleClose = () => {
  clearErrors();
  form.value = {
    with_pump_norm: '',
    without_pump_norm: '',
    km_norm: '',
    date: new Date().toISOString().split('T')[0]
  };
  emit('close');
};

defineExpose({
  handleClose
});
</script>
