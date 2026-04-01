
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
  
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Роли</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите название роли" class="mb-4" />
        <DataTable 
          :data="filteredRoles" 
          :columns="columns"
          :selectable="true"
          :show-select-all="false"
          :selected-rows="getSelectedIndexes()"
          @row-selected="onRowsSelected"
          @row-click="onRowClick"
        >
          <template v-if="auth.permissions.view_users" #cell-users="{ row }">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-sm" :style="{ color: palette.dark }">{{ getUsersForRole(row.id).count }}</span>
              <div class="flex items-center gap-1 text-sm">
                <span 
                  v-for="(user, idx) in getUsersForRole(row.id).usersList.slice(0, 3)"
                  :key="user.id"
                  :style="{ color: palette.primary }"
                  class="cursor-pointer hover:underline"
                  @click.stop="openUserEditModal(user)"
                >
                  {{ user.surname }} {{ user.name }}
                  <span v-if="idx < Math.min(2, getUsersForRole(row.id).usersList.length - 1)">, </span>
                </span>
                <span v-if="getUsersForRole(row.id).count > 3" class="text-gray-600" :title="getExtraUsersTooltip(row.id)">
                  и ещё {{ getUsersForRole(row.id).count - 3 }}
                </span>
              </div>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Error Modal -->
    <ErrorModal ref="errorModalRef" />

    <!-- Modal добавления роли -->
    <Modal
      :is-open="showAddModal"
      title="Добавить роль"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <TextInput 
          v-model="newRole.name" 
          :label="fieldDefinitions.role.name.label" 
          :hint="fieldDefinitions.role.name.hint"
          placeholder="Введите название роли"
          :required="fieldDefinitions.role.name.required"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeAddModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="addRole">Добавить</Button>
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

    <!-- Modal подтверждения удаления -->
    <Modal
      :is-open="showDeleteModal"
      title="Подтвердить удаление"
      @close="closeDeleteModal"
    >
      <div class="space-y-4">
        <p :style="{ color: palette.dark }">
          <span class="font-semibold">Внимание!</span> Вы собираетесь удалить следующие роли:
        </p>
        <div class="bg-red-50 border border-red-200 rounded p-4">
          <ul class="space-y-2">
            <li v-for="role in filteredRoles.filter(r => selectedRoleIds.includes(r.id))" :key="role.id" :style="{ color: palette.dark }">
              <span class="font-semibold">{{ role.name }}</span>
            </li>
          </ul>
        </div>

        <div v-if="usersWithRoles.length > 0" class="bg-yellow-50 border border-yellow-200 rounded p-4">
          <p :style="{ color: palette.dark }" class="font-semibold mb-2">Пользователи, связанные с этими ролями:</p>
          <ul class="space-y-1 text-sm">
            <li v-for="user in usersWithRoles" :key="user.id" :style="{ color: palette.dark }">
              {{ user.surname }} {{ user.name }} {{ user.last_name }} (Роль: {{ user.role_name }})
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeDeleteModal">Отмена</Button>
        <Button variant="primary" size="md" @click="confirmDelete">Удалить</Button>
      </template>
    </Modal>

    <!-- CRUD Panel -->
    <CrudPanel 
      @create="handleCrudCreate"
      @delete="handleCrudDelete"
      createLabel="Создать роль"
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
const errorModalRef = ref(null);
const roles = ref([]);
const selectedRoleIds = ref([]);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const userEditModal = ref(null);
const roleEditModal = ref(null);
const users = ref([]);
const { searchQuery, filtered: filteredRoles } = useSearch(roles, ['name']);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const usersWithRoles = ref([]);

const columns = computed(() => {
  const baseCols = [
    { key: 'name', label: 'Название роли' }
  ];
  // Добавляем столбец с пользователями только если есть право на просмотр
  if (auth.permissions.view_users) {
    baseCols.push({ key: 'users', label: 'Пользователи' });
  }
  return baseCols;
});


const newRole = ref({
  name: ''
});

const fetchRoles = async () => {
  try {
    const response = await axios.get('/roles/', { headers: { Authorization: `Bearer ${auth.access}` } });
    roles.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке ролей:', error);
  }
};

const fetchUsers = async () => {
  // Загружаем пользователей только если есть право на просмотр
  if (!auth.permissions.view_users) {
    return;
  }
  try {
    const response = await axios.get('/users/', { headers: { Authorization: `Bearer ${auth.access}` } });
    users.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке пользователей:', error);
  }
};

const getUsersForRole = (roleId) => {
  const roleUsers = users.value.filter(user => user.role === roleId);
  const names = roleUsers.map(u => `${u.surname} ${u.name}`).slice(0, 3);
  const count = roleUsers.length;
  let text = names.join(', ');
  if (count > 3) {
    text += ` и ещё ${count - 3}`;
  }
  return { 
    usersList: roleUsers,
    names: names, 
    count: count, 
    text: text || 'Нет пользователей' 
  };
};

const getExtraUsersTooltip = (roleId) => {
  const roleUsers = users.value.filter(user => user.role === roleId);
  return roleUsers.slice(3).map(u => `${u.surname} ${u.name}`).join(', ');
};

const openUserEditModal = (user) => {
  if (!auth.permissions.can_update_users && !auth.permissions.view_users) {
    permissionDeniedModal.value?.openModal('view_users');
    return;
  }
  userEditModal.value?.openModal(user, roles.value);
};

const onUserUpdated = (updatedUser) => {
  // Обновляем пользователя в списке
  const userIndex = users.value.findIndex(u => u.id === updatedUser.id);
  if (userIndex > -1) {
    users.value[userIndex] = updatedUser;
  }
};

const onRoleUpdated = (updatedRole) => {
  // Обновляем роль в списке
  const roleIndex = roles.value.findIndex(r => r.id === updatedRole.id);
  if (roleIndex > -1) {
    roles.value[roleIndex] = updatedRole;
  }
};

const getSelectedIndexes = () => {
  return filteredRoles.value
    .map((role, index) => selectedRoleIds.value.includes(role.id) ? index : -1)
    .filter(index => index !== -1);
};

const onRowsSelected = (selectedIndexes) => {
  selectedRoleIds.value = selectedIndexes.map(idx => filteredRoles.value[idx].id);
};

const openAddModal = () => {
  newRole.value = { name: '' };
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  newRole.value = { name: '' };
};

// Создание роли с автоматическим созданием Permission
const addRole = async () => {
  if (!auth.permissions.can_create_roles) {
    console.warn('Нет разрешения на создание ролей.');
    return;
  }

  // Полная валидация по field definitions
  const validationErrors = validateFormFields(newRole.value, fieldDefinitions.role);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    // 1. Создаём роль
    const roleResp = await axios.post('/roles/', newRole.value, { headers: { Authorization: `Bearer ${auth.access}` } });
    const createdRole = roleResp.data;
    roles.value.push(createdRole);

    // 2. Создаём Permission для этой роли (все поля false)
    const permissionPayload = { role: createdRole.id };
    const permResp = await axios.post('/permissions/', permissionPayload, { headers: { Authorization: `Bearer ${auth.access}` } });
    
    // 3. Открываем окно редактирования разрешений для новой роли
    showAddModal.value = false;
    roleEditModal.value?.openModal(createdRole, roles.value);
    
    // Сброс формы
    newRole.value = { name: '' };
  } catch (error) {
    console.error('Ошибка при создании роли или разрешений:', error);
    errorModalRef.value?.openModal(error);
  }
};

const onRowClick = (role) => {
  // Проверка прав доступа
  const canUpdateRoles = auth.permissions.can_update_roles;
  const canViewPermissions = auth.permissions.view_permissisons;

  // Если нет прав на обновление ролей и не может просматривать разрешения
  if (!canUpdateRoles && !canViewPermissions) {
    // Определяем какое право требуется
    const requiredPermission = 'can_update_roles';
    permissionDeniedModal.value?.openModal(requiredPermission);
    return;
  }

  roleEditModal.value?.openModal(role, roles.value);
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_roles && auth.permissions.can_create_permissions|| false,
    canDelete: auth.permissions.can_delete_roles && auth.permissions.can_delete_permissisons || false,
  });
};

const handleCrudCreate = () => {
  openAddModal();
};

const openDeleteModal = async () => {
  if (selectedRoleIds.value.length === 0) {
    noSelectionModal.value?.openModal();
    return;
  }
  
  // Загружаем пользователей, связанных с выбранными ролями (только если есть право на просмотр)
  if (auth.permissions.view_users) {
    try {
      const response = await axios.get('/users/', {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
      const allUsers = response.data;
      // Фильтруем пользователей, которые имеют одну из выбранных ролей
      usersWithRoles.value = allUsers.filter(user => 
        selectedRoleIds.value.includes(user.role)
      ).map(user => ({
        ...user,
        role_name: roles.value.find(r => r.id === user.role)?.name || '-'
      }));
    } catch (error) {
      console.error('Ошибка при загрузке пользователей:', error);
      usersWithRoles.value = [];
    }
  } else {
    console.warn('Нет разрешения на просмотр пользователей.');
    usersWithRoles.value = [];
  }
  
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
  usersWithRoles.value = [];
};

const confirmDelete = async () => {
  if (!auth.permissions.can_delete_roles) {
    permissionDeniedModal.value?.openModal('can_delete_roles');
    closeDeleteModal();
    return;
  }

  try {
    // Удаляем каждую выбранную роль и связанные разрешения
    for (const id of selectedRoleIds.value) {
      // Сначала загружаем разрешения для этой роли
      if (auth.permissions.can_delete_permissisons) {
        try {
          const permResponse = await axios.get(`/permissions/?role=${id}`, { 
            headers: { Authorization: `Bearer ${auth.access}` } 
          });
          // Удаляем все найденные разрешения для этой роли
          if (permResponse.data && permResponse.data.length > 0) {
            for (const permission of permResponse.data) {
              await axios.delete(`/permissions/${permission.id}/`, {
                headers: { Authorization: `Bearer ${auth.access}` }
              });
            }
          }
        } catch (error) {
          console.error('Ошибка при удалении разрешений для роли:', id, error);
        }
      }
      
      // Затем удаляем саму роль
      await axios.delete(`/roles/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[Roles] Roles and permissions deleted successfully');
    
    // Обновляем список ролей и очищаем выделение
    selectedRoleIds.value = [];
    await fetchRoles();
    closeDeleteModal();
  } catch (error) {
    console.error('Ошибка при удалении ролей:', error);
    alert('Ошибка при удалении ролей: ' + (error.response?.data?.detail || error.message));
  }
};

const deleteButtonLabel = computed(() => {
  const count = selectedRoleIds.value.length;
  if (count === 0) return 'Удалить роль';
  if (count === 1) return 'Удалить роль';
  return `Удалить роли (${count})`;
});

const isDeleteDisabled = computed(() => selectedRoleIds.value.length === 0);

const handleCrudDelete = () => {
  openDeleteModal();
};

onMounted(() => {
   setupCrudPermissions();
    console.log("[Roles] User permissions:", auth.permissions); 
   if (auth.permissions.view_roles) {
     fetchRoles();
  } else {
    console.warn("[Roles] User does not have permission to view roles.");
    permissionDeniedModal.value?.openModal('view_roles');
  }
  // Загружаем пользователей если есть право на просмотр
  if (auth.permissions.view_users) {
    fetchUsers();
  } else {
    permissionDeniedModal.value?.openModal('view_users');
  }
 });


onUnmounted(() => {
  auth.clearCrudPermissions();
}); 
</script>
