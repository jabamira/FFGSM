<template>
  <Modal
    :is-open="isOpen"
    title="Редактировать пользователя"
    @close="closeModal"
  >
    <div v-if="editingUser" class="space-y-4 min-w-96">
      <TextInput 
        v-model="editingUser.name" 
        label="Имя" 
        placeholder="Введите имя"
        :disabled="!auth.permissions.can_update_users"
        required
      />
      <TextInput 
        v-model="editingUser.surname" 
        label="Фамилия" 
        placeholder="Введите фамилию"
        :disabled="!auth.permissions.can_update_users"
        required
      />
      <TextInput 
        v-model="editingUser.last_name" 
        label="Отчество" 
        placeholder="Введите отчество"
        :disabled="!auth.permissions.can_update_users"
      />
      <TextInput 
        v-model="editingUser.login" 
        label="Логин" 
        placeholder="Введите логин"
        :disabled="!auth.permissions.can_update_users"
        required
      />
      <TextInput 
        v-model="editingUser.phone" 
        label="Телефон" 
        placeholder="Введите телефон"
        :disabled="!auth.permissions.can_update_users"
      />
      <SelectInput
        v-if="roles.length > 0"
        v-model="editingUser.role"
        label="Роль"
        :options="roleOptions"
        placeholder="Выберите роль"
        :disabled="!auth.permissions.can_update_users"
        required
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
import { useAuthStore } from '../stores/auth';
import axios from 'axios';

const auth = useAuthStore();
const isOpen = ref(false);
const editingUser = ref(null);
const originalUser = ref(null);
const roles = ref([]);

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
};

const updateUser = async () => {
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

  if (!editingUser.value.name || !editingUser.value.surname || !editingUser.value.login) {
    alert('Пожалуйста, заполните обязательные поля (Имя, Фамилия, Логин)');
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
    alert('Ошибка при обновлении пользователя: ' + (error.response?.data?.detail || error.message));
  }
};

const emit = defineEmits(['user-updated']);

defineExpose({
  openModal,
  closeModal
});
</script>
