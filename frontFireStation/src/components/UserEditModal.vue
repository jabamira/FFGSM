<template>
  <ErrorModal ref="errorModalRef" />
  
  <Modal
    :is-open="isOpen"
    title="Редактировать пользователя"
    @close="closeModal"
  >
    <div v-if="editingUser" class="space-y-4 min-w-96">
      <div v-if="generalError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
        <p class="text-sm font-semibold text-red-600">{{ generalError }}</p>
      </div>
      <TextInput 
        v-model="editingUser.name" 
        :label="fieldDefinitions.userEdit.name.label" 
        :hint="fieldDefinitions.userEdit.name.hint"
        :error="formErrors.name"
        placeholder="Введите имя"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.name.required"
      />
      <TextInput 
        v-model="editingUser.surname" 
        :label="fieldDefinitions.userEdit.surname.label" 
        :hint="fieldDefinitions.userEdit.surname.hint"
        :error="formErrors.surname"
        placeholder="Введите фамилию"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.surname.required"
      />
      <TextInput 
        v-model="editingUser.last_name" 
        :label="fieldDefinitions.userEdit.last_name.label" 
        :hint="fieldDefinitions.userEdit.last_name.hint"
        :error="formErrors.last_name"
        placeholder="Введите отчество"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.last_name.required"
      />
      <TextInput 
        v-model="editingUser.login" 
        :label="fieldDefinitions.userEdit.login.label" 
        :hint="fieldDefinitions.userEdit.login.hint"
        :error="formErrors.login"
        placeholder="Введите логин"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.login.required"
      />
      <TextInput 
        v-model="editingUser.password" 
        :label="fieldDefinitions.userEdit.password.label" 
        :hint="fieldDefinitions.userEdit.password.hint"
        :error="formErrors.password"
        placeholder="Введите пароль"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.password.required"
      />
      <TextInput 
        v-model="editingUser.phone" 
        :label="fieldDefinitions.userEdit.phone.label" 
        :hint="fieldDefinitions.userEdit.phone.hint"
        :error="formErrors.phone"
        placeholder="Введите телефон"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.phone.required"
      />
      <TextInput 
        v-model="editingUser.driver_license" 
        :label="fieldDefinitions.userEdit.driver_license.label" 
        :hint="fieldDefinitions.userEdit.driver_license.hint"
        :error="formErrors.driver_license"
        placeholder="Введите номер водительского удостоверения"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.driver_license.required"
      />
      <SelectInput
        v-if="roles.length > 0"
        v-model="editingUser.role"
        :label="fieldDefinitions.userEdit.role.label"
        :hint="fieldDefinitions.userEdit.role.hint"
        :error="formErrors.role"
        :options="roleOptions"
        placeholder="Выберите роль"
        :disabled="!auth.permissions.can_update_users"
        :required="fieldDefinitions.userEdit.role.required"
      />
    </div>

    <!-- Permission Denied Message -->
    <div v-if="!auth.permissions.can_update_users" class="rounded p-4 bg-yellow-50 border border-yellow-200">
      <p class="text-sm text-yellow-800">
        У вас нет прав на редактирование пользователей. Данные доступны только для просмотра.
      </p>
    </div>

    <template #footer>
      <Button variant="secondary" size="md" @click="closeModal">Закрыть</Button>
      <Button 
        v-if="auth.permissions.can_update_users"
        variant="primary" 
        size="md" 
        @click="updateUser"
        :disabled="!hasUserChanged()"
      >
        Сохранить
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, TextInput, SelectInput } from './ui/importUi';
import ErrorModal from './ErrorModal.vue';
import { useAuthStore } from '../stores/auth';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields, createValidationError } from '../utils/errorUtils';
import axios from 'axios';

const auth = useAuthStore();
const errorModalRef = ref(null);
const isOpen = ref(false);
const editingUser = ref(null);
const originalUser = ref(null);
const roles = ref([]);
const formErrors = ref({});
const generalError = ref('');

const roleOptions = computed(() => {
  return roles.value.map(role => ({
    value: role.id,
    label: role.name
  }));
});

const hasUserChanged = () => {
  if (!editingUser.value || !originalUser.value) return false;
  return JSON.stringify(editingUser.value) !== JSON.stringify(originalUser.value);
};

const openModal = async (user, allRoles) => {
  originalUser.value = { ...user };
  editingUser.value = { ...user };
  roles.value = allRoles || [];
  isOpen.value = true;
};

const closeModal = () => {
  isOpen.value = false;
  editingUser.value = null;
  originalUser.value = null;
  roles.value = [];
  formErrors.value = {};
  generalError.value = '';
};

const updateUser = async () => {
  formErrors.value = {};
  generalError.value = '';

  if (!auth.permissions.can_update_users) {
    console.warn('Нет разрешения на редактирование пользователей.');
    return;
  }

  if (!editingUser.value) return;

  // Проверяем, изменилась ли пользователь
  if (!hasUserChanged()) {
    console.log('[UserEditModal] No changes detected');
    closeModal();
    return;
  }

  // Полная валидация по field definitions
  const validationErrors = validateFormFields(editingUser.value, fieldDefinitions.userEdit);
  if (Object.keys(validationErrors).length > 0) {
    formErrors.value = validationErrors;
    generalError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  // Проверка разрешения перед отправкой
  if (!auth.permissions.can_update_users) {
    generalError.value = 'У вас нет прав на редактирование пользователей';
    return;
  }

  try {
    const response = await axios.put(`/users/${editingUser.value.id}/`, editingUser.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    // Эмитим событие успешного обновления
    emit('user-updated', response.data);
    closeModal();
  } catch (error) {
    console.error('Ошибка при обновлении пользователя:', error);
    errorModalRef.value?.openModal(error);
  }
};

const emit = defineEmits(['user-updated']);

defineExpose({
  openModal,
  closeModal
});
</script>
