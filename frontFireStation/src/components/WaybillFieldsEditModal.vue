<template>
  <Modal
    :isOpen="showModal"
    title="Редактировать путевой лист"
    @close="closeModal"
  >
    <div class="space-y-4">
      <SelectInput
        v-model="form.car"
        :options="carOptions"
        label="Автомобиль"
        :required="true"
      />
      <SelectInput
        v-model="form.driver"
        :options="driverOptions"
        label="Водитель"
        :required="true"
      />
      <SelectInput
        v-model="form.norm_season"
        :options="[
          { value: 'summer', label: 'Лето' },
          { value: 'winter', label: 'Зима' }
        ]"
        label="Сезон"
        :required="true"
      />
      <DateInput
        v-model="form.date"
        label="Дата"
        :required="true"
      />
      <span v-if="validationError" style="color: red; font-size: 0.875rem">{{ validationError }}</span>
    </div>
    <template #footer>
      <Button @click="closeModal" variant="secondary">Отмена</Button>
      <Button 
        @click="submitEdit" 
        variant="primary"
        :disabled="isSaveButtonDisabled"
      >
        Сохранить
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, SelectInput, DateInput } from './ui/importUi';

const props = defineProps({
  carOptions: {
    type: Array,
    required: true
  },
  driverOptions: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['edit']);

// Modal state
const showModal = ref(false);

// Form data
const form = ref({
  id: null,
  car: null,
  driver: null,
  date: new Date().toISOString().split('T')[0],
  norm_season: 'summer'
});

// Original data for comparison
const originalData = ref({
  id: null,
  car: null,
  driver: null,
  date: new Date().toISOString().split('T')[0],
  norm_season: 'summer'
});

const validationError = ref('');

// Computed properties
const isSaveButtonDisabled = computed(() => {
  return JSON.stringify(form.value) === JSON.stringify(originalData.value);
});

// Methods
const openEditModal = (waybill) => {
  validationError.value = '';
  form.value = {
    id: waybill.id,
    car: waybill.car,
    driver: waybill.driver,
    date: waybill.date,
    norm_season: waybill.norm_season
  };
  
  // Store original data for comparison
  originalData.value = JSON.parse(JSON.stringify(form.value));
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const submitEdit = async () => {
  if (!form.value.car || !form.value.driver) {
    validationError.value = 'Пожалуйста, выберите автомобиль и водителя';
    return;
  }

  try {
    await emit('edit', {
      id: form.value.id,
      car: form.value.car,
      driver: form.value.driver,
      date: form.value.date,
      norm_season: form.value.norm_season
    });
    closeModal();
  } catch (error) {
    validationError.value = error.message || 'Произошла ошибка при сохранении';
  }
};

// Expose methods
defineExpose({
  openEditModal,
  closeModal
});
</script>
