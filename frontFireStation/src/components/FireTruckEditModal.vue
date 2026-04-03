<template>
  <Modal
    :is-open="isOpen"
    title="Редактировать пожарный автомобиль"
    @close="$emit('close')"
  >
    <div v-if="fireTruck" class="space-y-4 min-w-96">
      <div v-if="generalError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
        <p class="text-sm font-semibold text-red-600">{{ generalError }}</p>
      </div>
      <TextInput 
        v-model="fireTruck.number" 
        :label="fieldDefinitions.fireTruck.number.label" 
        :hint="fieldDefinitions.fireTruck.number.hint"
        placeholder="Введите гос. номер"
        :required="fieldDefinitions.fireTruck.number.required"
        :uppercase="fieldDefinitions.fireTruck.number.uppercase"
        :error="formErrors.number"
      />
      <TextInput 
        v-model="fireTruck.brand" 
        :label="fieldDefinitions.fireTruck.brand.label" 
        :hint="fieldDefinitions.fireTruck.brand.hint"
        placeholder="Введите марку"
        :required="fieldDefinitions.fireTruck.brand.required"
        :error="formErrors.brand"
      />
      <TextInput 
        v-model="fireTruck.model" 
        :label="fieldDefinitions.fireTruck.model.label" 
        :hint="fieldDefinitions.fireTruck.model.hint"
        placeholder="Введите модель"
        :required="fieldDefinitions.fireTruck.model.required"
        :error="formErrors.model"
      />
      <TextInput 
        v-model="fireTruck.type" 
        :label="fieldDefinitions.fireTruck.type.label" 
        :hint="fieldDefinitions.fireTruck.type.hint"
        placeholder="Введите тип"
        :required="fieldDefinitions.fireTruck.type.required"
        :error="formErrors.type"
      />
      <SelectInput 
        v-model="fireTruck.fuel_type" 
        :label="fieldDefinitions.fireTruck.fuel_type.label" 
        :hint="fieldDefinitions.fireTruck.fuel_type.hint"
        :options="fuelTypeOptions"
        placeholder="Выберите тип топлива"
        :required="fieldDefinitions.fireTruck.fuel_type.required"
        :error="formErrors.fuel_type"
      />
    </div>
    <template #footer>
      <Button 
        v-if="fireTruck && !hasOdometer && canViewFireTrucks"
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
  truck: {
    type: Object,
    default: null,
  },
  originalTruck: {
    type: Object,
    default: null,
  },
  hasOdometer: {
    type: Boolean,
    default: false,
  },
  canViewFireTrucks: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close', 'save', 'odometer-click']);

const fireTruck = ref(null);
const formErrors = ref({});
const generalError = ref('');

watch(
  () => props.truck,
  (newTruck) => {
    if (newTruck) {
      fireTruck.value = { ...newTruck };
    }
  },
  { immediate: true }
);

const hasChanged = computed(() => {
  if (!fireTruck.value || !props.originalTruck) return false;
  return JSON.stringify(fireTruck.value) !== JSON.stringify(props.originalTruck);
});

watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen && props.truck) {
      fireTruck.value = { ...props.truck };
      formErrors.value = {};
      generalError.value = '';
    }
  }
);

const getTruck = () => fireTruck.value;

const clearErrors = () => {
  formErrors.value = {};
  generalError.value = '';
};

const setErrors = (errors, message = '') => {
  formErrors.value = errors;
  generalError.value = message;
};

defineExpose({
  getTruck,
  clearErrors,
  setErrors,
});
</script>
