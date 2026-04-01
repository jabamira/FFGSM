<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Пользователи</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <div class="grid grid-cols-1 gap-4 mb-4" :class="auth.permissions.view_roles ? 'md:grid-cols-2' : ''">
          <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите ФИО, логин или телефон" />
          <SelectInput 
            v-if="auth.permissions.view_roles"
            v-model="selectedRoleFilter" 
            label="Фильтр по роли" 
            :options="roleFilterOptions"
            placeholder="Все роли"
          />
        </div>
        <DataTable 
          :data="filteredUsersByRole" 
          :columns="columns"
          :selectable="true"
          :show-select-all="false"
          :selected-rows="getSelectedIndexes()"
          @row-selected="onRowsSelected"
          @row-click="onRowClick"
        >
          <template v-if="auth.permissions.view_roles" #cell-role_name="{ row }">
            <span 
              v-if="auth.permissions.can_update_roles || auth.permissions.can_update_permissisons"
              :style="{ color: palette.primary }"
              class="cursor-pointer hover:underline"
              @click.stop="openRoleEditModal(row.role)"
            >
              {{ row.role_name }}
            </span>
            <span v-else>
              {{ row.role_name }}
            </span>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Error Modal -->
    <ErrorModal ref="errorModalRef" />

    <!-- Modal добавления пользователя -->
    <Modal
      :is-open="showAddModal"
      title="Добавить пользователя"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <TextInput 
          v-model="newUser.name" 
          :label="fieldDefinitions.userCreate.name.label" 
          :hint="fieldDefinitions.userCreate.name.hint"
          placeholder="Введите имя"
          :required="fieldDefinitions.userCreate.name.required"
        />
        <TextInput 
          v-model="newUser.surname" 
          :label="fieldDefinitions.userCreate.surname.label" 
          :hint="fieldDefinitions.userCreate.surname.hint"
          placeholder="Введите фамилию"
          :required="fieldDefinitions.userCreate.surname.required"
        />
        <TextInput 
          v-model="newUser.last_name" 
          :label="fieldDefinitions.userCreate.last_name.label" 
          :hint="fieldDefinitions.userCreate.last_name.hint"
          placeholder="Введите отчество"
          :required="fieldDefinitions.userCreate.last_name.required"
        />
        <TextInput 
          v-model="newUser.login" 
          :label="fieldDefinitions.userCreate.login.label" 
          :hint="fieldDefinitions.userCreate.login.hint"
          placeholder="Введите логин"
          :required="fieldDefinitions.userCreate.login.required"
        />
        <TextInput 
          v-model="newUser.password" 
          :label="fieldDefinitions.userCreate.password.label" 
          :hint="fieldDefinitions.userCreate.password.hint"
          placeholder="Введите пароль"
          type="password"
          :required="fieldDefinitions.userCreate.password.required"
        />
        <TextInput 
          v-model="newUser.phone" 
          :label="fieldDefinitions.userCreate.phone.label" 
          :hint="fieldDefinitions.userCreate.phone.hint"
          placeholder="Введите телефон"
          :required="fieldDefinitions.userCreate.phone.required"
        />
        <TextInput 
          v-model="newUser.driver_license" 
          :label="fieldDefinitions.userCreate.driver_license.label" 
          :hint="fieldDefinitions.userCreate.driver_license.hint"
          placeholder="Введите номер удостоверения (опционально)"
          :required="fieldDefinitions.userCreate.driver_license.required"
        />
        <SelectInput 
          v-if="auth.permissions.view_roles"
          v-model="newUser.role" 
          :label="fieldDefinitions.userCreate.role.label"
          :hint="fieldDefinitions.userCreate.role.hint"
          :options="roleOptions"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeAddModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="addUser">Добавить</Button>
      </template>
    </Modal>

    <!-- Modal подтверждения удаления -->
    <Modal
      :is-open="showDeleteModal"
      title="Подтвердить удаление"
      @close="closeDeleteModal"
    >
      <div class="space-y-4">
        <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующих пользователей:</p>
          <div class="max-w-full mx-auto mt-8 mb-4 text-sm text-gray-500">

          </div>
        <div class="bg-red-50 border border-red-200 rounded p-4">
          <ul class="space-y-2">
            <li v-for="user in usersToDelete" :key="user.id" :style="{ color: palette.dark }">
              {{ user.surname }} {{ user.name }} {{ user.last_name }}
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeDeleteModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="confirmDelete">Удалить</Button>
      </template>
    </Modal>

    <!-- Permission Denied Modal -->
    <PermissionDeniedModal ref="permissionDeniedModal" />

    <!-- No Selection Modal -->
    <NoSelectionModal ref="noSelectionModal" />

    <!-- User Edit Modal -->
    <UserEditModal ref="userEditModal" @user-updated="onUserUpdated" />

    <!-- Role Edit Modal -->
    <RoleEditModal ref="roleEditModal" @role-updated="onRoleUpdated" />

    <!-- CRUD Panel -->
    <CrudPanel 
      @create="handleCrudCreate"
      @delete="handleCrudDelete"
      createLabel="Создать пользователя"
      :deleteLabel="deleteButtonLabel"
      :isDeleteDisabled="isDeleteDisabled"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { DataTable, TextInput, palette, Modal, Button, SelectInput } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import { useSearch } from '../composables/useSearch';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields, createValidationError } from '../utils/errorUtils';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';
import ErrorModal from '../components/ErrorModal.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import NoSelectionModal from '../components/NoSelectionModal.vue';
import UserEditModal from '../components/UserEditModal.vue';
import RoleEditModal from '../components/RoleEditModal.vue';
import CrudPanel from '../components/CrudPanel.vue';

const auth = useAuthStore();
const users = ref([]);
const roles = ref([]);
const selectedUserIds = ref([]);
const errorModalRef = ref(null);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const userEditModal = ref(null);
const roleEditModal = ref(null);
const { searchQuery, filtered: filteredUsers } = useSearch(users, ['name', 'surname', 'last_name', 'login', 'phone']);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);
const editingUser = ref(null);
const originalUser = ref(null);
const selectedRoleFilter = ref(null);

const columns = computed(() => {
  const baseCols = [
    { key: 'name', label: 'Имя' },
    { key: 'surname', label: 'Фамилия' },
    { key: 'last_name', label: 'Отчество' },
    { key: 'login', label: 'Логин' },
    { key: 'phone', label: 'Телефон' }
  ];
  
  if (auth.permissions.view_roles) {
    baseCols.push({ key: 'role_name', label: 'Роль' });
  }
  
  return baseCols;
});

const newUser = ref({
  name: '',
  surname: '',
  last_name: '',
  login: '',
  password: '',
  phone: '',
  driver_license: '',
  role: null,
});



const roleOptions = computed(() => {
  return roles.value.map(role => ({
    value: role.id,
    label: role.name
  }));
});

const roleFilterOptions = computed(() => {
  return [
    { value: null, label: 'Все роли' },
    ...roles.value.map(role => ({
      value: role.id,
      label: role.name
    }))
  ];
});

const fetchRoles = async () => {
  try {
    const response = await axios.get('/roles/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    roles.value = response.data;
    console.log('[Users] Roles loaded:', roles.value);
  } catch (error) {
    console.error('Ошибка при загрузке ролей:', error);
  }
};

const fetchUsers = async () => {
  if (!auth.permissions.view_users) {
    console.warn('Нет разрешения на просмотр пользователей (view_users).');
    return;
  }

  try {
    const response = await axios.get('/users/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    // Добавляем role_name для отображения в таблице
    users.value = response.data.map(user => ({
      ...user,
      role_name: roles.value.find(r => r.id === user.role)?.name || '-'
    }));
  } catch (error) {
    console.error('Ошибка при загрузке пользователей:', error);
  }
};


const filteredUsersByRole = computed(() => {
  if (!selectedRoleFilter.value) {
    return filteredUsers.value;
  }
  return filteredUsers.value.filter(u => u.role === selectedRoleFilter.value);
});

const usersToDelete = computed(() => {
  return filteredUsersByRole.value.filter(u => selectedUserIds.value.includes(u.id));
});

const getSelectedIndexes = () => {
  return filteredUsersByRole.value
    .map((user, index) => selectedUserIds.value.includes(user.id) ? index : -1)
    .filter(index => index !== -1);
};

const onRowsSelected = (selectedIndexes) => {
  selectedUserIds.value = selectedIndexes.map(idx => filteredUsersByRole.value[idx].id);
};

const openAddModal = () => {
  resetNewUser();
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  resetNewUser();
};

const resetNewUser = () => {
  newUser.value = {
    name: '',
    surname: '',
    last_name: '',
    login: '',
    password: '',
    phone: '',
    driver_license: '',
    role: auth.permissions.view_roles ? null : undefined,
  };
};

const addUser = async () => {
  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на создание пользователей.');
    return;
  }

  // Полная валидация по field definitions
  const validationErrors = validateFormFields(newUser.value, fieldDefinitions.userCreate);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    const userData = { ...newUser.value };
    // Убираем роль если она не требуется
    if (!auth.permissions.view_roles) {
      delete userData.role;
    }
    
    const response = await axios.post('/users/', userData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[Users] User added successfully:', response.data);
    const newUserData = {
      ...response.data,
      role_name: roles.value.find(r => r.id === response.data.role)?.name || '-'
    };
    users.value.push(newUserData);
    closeAddModal();
  } catch (error) {
    console.error('Ошибка при добавлении пользователя:', error);
    errorModalRef.value?.openModal(error);
  }
};

const openEditModal = async (user) => {
  editingUser.value = { ...user, password: '' };
  originalUser.value = { ...user, password: '' };
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingUser.value = null;
  originalUser.value = null;
};

const hasUserChanged = () => {
  if (!editingUser.value || !originalUser.value) return false;
  return JSON.stringify(editingUser.value) !== JSON.stringify(originalUser.value);
};



const updateUser = async () => {
  if (!auth.permissions.can_update_users) {
    console.warn('Нет разрешения на редактирование пользователей.');
    return;
  }

  if (!editingUser.value) return;

  // Проверяем, изменились ли данные
  if (!hasUserChanged()) {
    console.log('[Users] No changes detected');
    closeEditModal();
    return;
  }

  // Валидация полей с использованием userEdit определений
  const validationErrors = validateFormFields(editingUser.value, fieldDefinitions.userEdit);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    const updateData = { ...editingUser.value };
    if (!updateData.password) {
      delete updateData.password;
    }
    // Убираем роль если нет прав на просмотр ролей
    if (!auth.permissions.view_roles) {
      delete updateData.role;
    }

    // Обновляем пользователя
    const response = await axios.put(`/users/${editingUser.value.id}/`, updateData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[Users] User updated successfully:', response.data);
    
    // Обновляем пользователя в таблице
    const userIndex = users.value.findIndex(u => u.id === editingUser.value.id);
    if (userIndex > -1) {
      const updatedUser = {
        ...response.data,
        role_name: roles.value.find(r => r.id === response.data.role)?.name || '-'
      };
      users.value[userIndex] = updatedUser;
    }
    
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при обновлении пользователя:', error);
    alert('Ошибка при обновлении пользователя: ' + (error.response?.data?.detail || error.message));
  }
};

const onRowClick = (user) => {
  // Проверка прав доступа
  const canUpdateUsers = auth.permissions.can_update_users;

  // Если нет прав на обновление пользователей
  if (!canUpdateUsers) {
    permissionDeniedModal.value?.openModal('can_update_users');
    return;
  }

  openUserEditModal(user);
};

const openUserEditModal = (user) => {
  userEditModal.value?.openModal(user, roles.value);
};

const openRoleEditModal = (roleId) => {
  if (!auth.permissions.can_update_roles && !auth.permissions.can_update_permissisons) {
    permissionDeniedModal.value?.openModal('can_update_roles');
    return;
  }
  const role = roles.value.find(r => r.id === roleId);
  if (role) {
    roleEditModal.value?.openModal(role);
  }
};

const onUserUpdated = (updatedUser) => {
  // Обновляем пользователя в списке
  const userIndex = users.value.findIndex(u => u.id === updatedUser.id);
  if (userIndex > -1) {
    const newUserData = {
      ...updatedUser,
      role_name: roles.value.find(r => r.id === updatedUser.role)?.name || '-'
    };
    users.value[userIndex] = newUserData;
  }
};

const onRoleUpdated = (updatedRole) => {
  // Обновляем роль в списке
  const roleIndex = roles.value.findIndex(r => r.id === updatedRole.id);
  if (roleIndex > -1) {
    roles.value[roleIndex] = updatedRole;
    // Обновляем role_name для всех пользователей с этой ролью
    users.value.forEach(user => {
      if (user.role === updatedRole.id) {
        user.role_name = updatedRole.name;
      }
    });
  }
};

const getRoleNameById = (roleId) => {
  return roles.value.find(r => r.id === roleId)?.name || '-';
};

const deleteButtonLabel = computed(() => {
  const count = selectedUserIds.value.length;
  if (count === 0) return 'Удалить пользователя';
  if (count === 1) return 'Удалить пользователя';
  return `Удалить пользователей (${count})`;
});

const isDeleteDisabled = computed(() => selectedUserIds.value.length === 0);

const openDeleteModal = () => {
  if (selectedUserIds.value.length === 0) {
    noSelectionModal.value?.openModal();
    return;
  }
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const confirmDelete = async () => {
  if (!auth.permissions.can_delete_users) {
    permissionDeniedModal.value?.openModal('can_delete_users');
    closeDeleteModal();
    return;
  }

  try {
    // Удаляем каждого выбранного пользователя
    for (const id of selectedUserIds.value) {
      await axios.delete(`/users/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[Users] Users deleted successfully');
    
    // Перезагружаем список пользователей и очищаем выделение
    selectedUserIds.value = [];
    await fetchUsers();
    closeDeleteModal();
  } catch (error) {
    console.error('Ошибка при удалении пользователей:', error);
  }
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_users || false,
    canDelete: auth.permissions.can_delete_users || false,
  });
};

const handleCrudCreate = () => {
  openAddModal();
};

const handleCrudDelete = () => {
  openDeleteModal();
};

onMounted(async () => {
  console.debug("[Users] Permissions loaded from store:", auth.permissions);
  setupCrudPermissions();
  
  // Загружаем роли первыми, чтобы они были доступны при загрузке пользователей
  if (auth.permissions.view_roles) {
    await fetchRoles();
  }
  
  if (auth.permissions.view_users) {
    await fetchUsers();
  } else {
    console.warn("[Users] User does not have permission to view users.");
    permissionDeniedModal.value?.openModal('view_users');
  }
});

onUnmounted(() => {
  auth.clearCrudPermissions();
});
</script>
