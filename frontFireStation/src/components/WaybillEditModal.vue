<template>
  <div>
    <!-- Add Modal -->
    <Modal
      :isOpen="showAddModal"
      title="Создать путевой лист"
      @close="closeAddModal"
    >
      <div class="space-y-4">
        <SelectInput
          v-model="form.car"
          :options="carOptions"
          label="Автомобиль"
          :required="true"
          placeholder="Выберите автомобиль"
        />
        <SelectInput
          v-model="form.driver"
          :options="driverOptions"
          label="Водитель"
          :required="true"
          placeholder="Выберите водителя"
        />
        <TextInput
          v-model="form.date"
          type="date"
          label="Дата"
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
        <SelectInput
          v-model="form.fuel_type"
          :options="fuelTypeOptions"
          label="Тип топлива"
          :required="true"
        />
        <span v-if="validationError" style="color: red; font-size: 0.875rem">{{ validationError }}</span>
      </div>
      <template #footer>
        <Button @click="closeAddModal" variant="secondary">Отмена</Button>
        <Button @click="submitAdd" variant="primary">Создать</Button>
      </template>
    </Modal>

    <!-- Edit Modal -->
    <Modal
      :isOpen="showEditModal"
      title="Редактировать путевой лист"
      @close="closeEditModal"
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
        <TextInput
          v-model="form.date"
          type="date"
          label="Дата"
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
        <SelectInput
          v-model="form.fuel_type"
          :options="fuelTypeOptions"
          label="Тип топлива"
          :required="true"
        />
        <span v-if="validationError" style="color: red; font-size: 0.875rem">{{ validationError }}</span>
      </div>
      <template #footer>
        <Button @click="closeEditModal" variant="secondary">Отмена</Button>
        <Button @click="submitEdit" variant="primary">Сохранить</Button>
      </template>
    </Modal>

    <!-- Delete Modal -->
    <Modal
      :isOpen="showDeleteModal"
      title="Подтверждение удаления"
      @close="closeDeleteModal"
    >
      <p>Вы уверены, что хотите удалить {{ deleteCount }} путевой(ые) лист(ы)?</p>
      <template #footer>
        <Button @click="closeDeleteModal" variant="secondary">Отмена</Button>
        <Button @click="submitDelete" variant="danger">Удалить</Button>
      </template>
    </Modal>

    <!-- Error Modal -->
    <ErrorModal
      :isOpen="showErrorModal"
      :title="errorModalTitle"
      :message="errorModalMessage"
      @close="showErrorModal = false"
    />

    <!-- Permission Denied Modal -->
    <PermissionDeniedModal
      ref="permissionModal"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, TextInput, SelectInput } from './ui/importUi';
import ErrorModal from './ErrorModal.vue';
import PermissionDeniedModal from './PermissionDeniedModal.vue';
import { fuelTypeOptions } from '../config/fuelTypes';

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

const emit = defineEmits(['add', 'edit', 'delete']);

// Modal states
const showAddModal = ref(false);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const showErrorModal = ref(false);
const errorModalTitle = ref('');
const errorModalMessage = ref('');

// Form data
const form = ref({
  id: null,
  car: null,
  driver: null,
  date: new Date().toISOString().split('T')[0],
  norm_season: 'summer',
  fuel_type: 'petrol95'
});

const validationError = ref('');
const deleteCount = ref(0);
const permissionModal = ref(null);

// Methods
const openAddModal = () => {
  validationError.value = '';
  form.value = {
    id: null,
    car: null,
    driver: null,
    date: new Date().toISOString().split('T')[0],
    norm_season: 'summer',
    fuel_type: 'petrol95'
  };
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
};

const openEditModal = (waybill) => {
  validationError.value = '';
  form.value = {
    id: waybill.id,
    car: waybill.car_id,
    driver: waybill.driver_id,
    date: waybill.date,
    norm_season: waybill.norm_season,
    fuel_type: waybill.fuel_type
  };
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
};

const openDeleteModal = (count) => {
  deleteCount.value = count;
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const submitAdd = async () => {
  if (!form.value.car || !form.value.driver) {
    validationError.value = 'Пожалуйста, выберите автомобиль и водителя';
    return;
  }

  try {
    await emit('add', {
      car_id: form.value.car,
      driver_id: form.value.driver,
      date: form.value.date,
      norm_season: form.value.norm_season,
      fuel_type: form.value.fuel_type
    });
    closeAddModal();
  } catch (error) {
    errorModalTitle.value = 'Ошибка создания путевого листа';
    errorModalMessage.value = error.message || 'Произошла ошибка';
    showErrorModal.value = true;
  }
};

const submitEdit = async () => {
  if (!form.value.car || !form.value.driver) {
    validationError.value = 'Пожалуйста, выберите автомобиль и водителя';
    return;
  }

  try {
    await emit('edit', {
      id: form.value.id,
      car_id: form.value.car,
      driver_id: form.value.driver,
      date: form.value.date,
      norm_season: form.value.norm_season,
      fuel_type: form.value.fuel_type
    });
    closeEditModal();
  } catch (error) {
    errorModalTitle.value = 'Ошибка обновления путевого листа';
    errorModalMessage.value = error.message || 'Произошла ошибка';
    showErrorModal.value = true;
  }
};

const submitDelete = () => {
  emit('delete');
  closeDeleteModal();
};

const showError = (title, message) => {
  errorModalTitle.value = title;
  errorModalMessage.value = message;
  showErrorModal.value = true;
};

const showPermissionError = () => {
  permissionModal.value?.openModal();
};

// Expose methods
defineExpose({
  openAddModal,
  openEditModal,
  openDeleteModal,
  showError,
  showPermissionError
});
</script>
