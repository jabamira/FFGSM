<template>
  <Modal
    :is-open="isOpen"
    title="Редактировать легковой автомобиль"
    @close="$emit('close')"
  >
    <div v-if="passengerCar" class="space-y-4 min-w-96">
      <div v-if="generalError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
        <p class="text-sm font-semibold text-red-600">{{ generalError }}</p>
      </div>
      <TextInput 
        v-model="passengerCar.number" 
        :label="fieldDefinitions.passengerCar.number.label" 
        :hint="fieldDefinitions.passengerCar.number.hint"
        :error="formErrors.number"
        placeholder="Введите гос. номер"
        :required="fieldDefinitions.passengerCar.number.required"
        :uppercase="fieldDefinitions.passengerCar.number.uppercase"
      />
      <TextInput 
        v-model="passengerCar.brand" 
        :label="fieldDefinitions.passengerCar.brand.label" 
        :hint="fieldDefinitions.passengerCar.brand.hint"
        :error="formErrors.brand"
        placeholder="Введите марку"
        :required="fieldDefinitions.passengerCar.brand.required"
      />
      <TextInput 
        v-model="passengerCar.model" 
        :label="fieldDefinitions.passengerCar.model.label" 
        :hint="fieldDefinitions.passengerCar.model.hint"
        :error="formErrors.model"
        placeholder="Введите модель"
        :required="fieldDefinitions.passengerCar.model.required"
      />
      <SelectInput 
        v-model="passengerCar.fuel_type" 
        :label="fieldDefinitions.passengerCar.fuel_type.label" 
        :hint="fieldDefinitions.passengerCar.fuel_type.hint"
        :error="formErrors.fuel_type"
        :options="fuelTypeOptions"
        placeholder="Выберите тип топлива"
        :required="fieldDefinitions.passengerCar.fuel_type.required"
      />
    </div>
    <template #footer>
      <Button 
        v-if="passengerCar && !hasOdometer && canViewPassengerCars"
        variant="secondary" 
        size="md" 
        @click="$emit('odometer-click')"
      >
        Внести стартовые данные
      </Button>
      <Button variant="secondary" size="md" @click="$emit('close')">Закрыть</Button>
      <Button variant="primary" size="md" @click="$emit('save')" :disabled="!hasChanged">Сохранить</Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Modal, TextInput, SelectInput, Button } from './ui/importUi';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { fuelTypeOptions } from '../config/fuelTypes';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  car: {
    type: Object,
    default: null,
  },
  originalCar: {
    type: Object,
    default: null,
  },
  hasOdometer: {
    type: Boolean,
    default: false,
  },
  canViewPassengerCars: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close', 'save', 'odometer-click']);

const passengerCar = ref(null);
const formErrors = ref({});
const generalError = ref('');

watch(
  () => props.car,
  (newCar) => {
    if (newCar) {
      passengerCar.value = { ...newCar };
    }
  },
  { immediate: true }
);

const hasChanged = computed(() => {
  if (!passengerCar.value || !props.originalCar) return false;
  return JSON.stringify(passengerCar.value) !== JSON.stringify(props.originalCar);
});

watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen && props.car) {
      passengerCar.value = { ...props.car };
      formErrors.value = {};
      generalError.value = '';
    }
  }
);

const getCar = () => passengerCar.value;

const clearErrors = () => {
  formErrors.value = {};
  generalError.value = '';
};

const setErrors = (errors, message = '') => {
  formErrors.value = errors;
  generalError.value = message;
};

defineExpose({
  getCar,
  clearErrors,
  setErrors,
});
</script>
