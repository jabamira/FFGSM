<template>
  <div>
    <!-- Add Modal -->
    <Modal
      :isOpen="showAddModal"
      title="Создать норму"
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
          v-model="form.season"
          :options="[
            { value: 'summer', label: 'Лето' },
            { value: 'winter', label: 'Зима' }
          ]"
          label="Сезон"
          :required="true"
        />
        <TextInput
          v-model="form.city_norm"
          type="number"
          step="0.01"
          label="Норма для города (л/100км)"
          :required="true"
          placeholder="0.00"
        />
        <TextInput
          v-model="form.area_norm"
          type="number"
          step="0.01"
          label="Норма для трассы (л/100км)"
          :required="true"
          placeholder="0.00"
        />
        <TextInput
          v-model="form.date"
          type="date"
          label="Дата действия"
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
      title="Редактировать норму"
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
          v-model="form.season"
          :options="[
            { value: 'summer', label: 'Лето' },
            { value: 'winter', label: 'Зима' }
          ]"
          label="Сезон"
          :required="true"
        />
        <TextInput
          v-model="form.city_norm"
          type="number"
          step="0.01"
          label="Норма для города (л/100км)"
          :required="true"
        />
        <TextInput
          v-model="form.area_norm"
          type="number"
          step="0.01"
          label="Норма для трассы (л/100км)"
          :required="true"
        />
        <TextInput
          v-model="form.date"
          type="date"
          label="Дата действия"
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
      <p>Вы уверены, что хотите удалить {{ deleteCount }} норм(ы)?</p>
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

const props = defineProps({
  carOptions: {
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
  season: 'summer',
  city_norm: '',
  area_norm: '',
  date: ''
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
    season: 'summer',
    city_norm: '',
    area_norm: '',
    date: ''
  };
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
};

const openEditModal = (norm) => {
  validationError.value = '';
  form.value = {
    id: norm.id,
    car: norm.car_id,
    season: norm.season,
    city_norm: norm.city_norm,
    area_norm: norm.area_norm,
    date: norm.date || ''
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
  if (!form.value.car || !form.value.city_norm || !form.value.area_norm) {
    validationError.value = 'Пожалуйста, заполните все необходимые поля';
    return;
  }

  try {
    await emit('add', {
      car_id: form.value.car,
      season: form.value.season,
      city_norm: parseFloat(form.value.city_norm),
      area_norm: parseFloat(form.value.area_norm),
      date: form.value.date || null
    });
    closeAddModal();
  } catch (error) {
    errorModalTitle.value = 'Ошибка создания норм';
    errorModalMessage.value = error.message || 'Произошла ошибка';
    showErrorModal.value = true;
  }
};

const submitEdit = async () => {
  if (!form.value.car || !form.value.city_norm || !form.value.area_norm) {
    validationError.value = 'Пожалуйста, заполните все необходимые поля';
    return;
  }

  try {
    await emit('edit', {
      id: form.value.id,
      car_id: form.value.car,
      season: form.value.season,
      city_norm: parseFloat(form.value.city_norm),
      area_norm: parseFloat(form.value.area_norm),
      date: form.value.date || null
    });
    closeEditModal();
  } catch (error) {
    errorModalTitle.value = 'Ошибка обновления норм';
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
