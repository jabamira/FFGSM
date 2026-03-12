
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
  
    <div class="p-6 max-w-6xl mx-auto pb-24">
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

    <!-- Modal добавления роли -->
    <Modal
      :is-open="showAddModal"
      title="Добавить роль"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <TextInput 
          v-model="newRole.name" 
          label="Название роли" 
          placeholder="Введите название роли"
          required
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { DataTable, TextInput, palette, Modal, Button, SelectInput } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import { useSearch } from '../composables/useSearch';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import NoSelectionModal from '../components/NoSelectionModal.vue';
import UserEditModal from '../components/UserEditModal.vue';
import RoleEditModal from '../components/RoleEditModal.vue';

const auth = useAuthStore();
const roles = ref([]);
const selectedRoleIds = ref([]);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const userEditModal = ref(null);
const roleEditModal = ref(null);
const users = ref([]);
const { searchQuery, filtered: filteredRoles } = useSearch(roles, ['name']);
const showAddModal = ref(false);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const editingRole = ref(null);
const originalRole = ref(null);
const rolePermissions = ref({});
const originalRolePermissions = ref({});
const permissionFields = ref([]);
const permissionSearchQuery = ref('');
const selectedPermissionGroup = ref('all');
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



const permissionsMap = {
  'can_use_mobile_booking': 'Может использовать мобильное приложение',
  'can_create_users': 'Может создавать пользователей',
  'can_delete_users': 'Может удалять пользователей',
  'can_update_users': 'Может обновлять пользователей',
  'view_users': 'Может просматривать пользователей',
  'view_drivers': 'Может просматривать водителей',
  'can_create_roles': 'Может создавать роли',
  'can_delete_roles': 'Может удалять роли',
  'can_update_roles': 'Может обновлять роли',
  'can_view_roles': 'Может просматривать роли',
  'can_create_permissions': 'Может создавать разрешения',
  'can_delete_permissisons': 'Может удалять разрешения',
  'can_update_permissisons': 'Может обновлять разрешения',
  'can_view_permissisons': 'Может просматривать разрешения',
  'can_create_fire_trucks': 'Может создавать пожарные машины',
  'can_delete_fire_trucks': 'Может удалять пожарные машины',
  'can_update_fire_trucks': 'Может обновлять пожарные машины',
  'view_fire_trucks': 'Может просматривать пожарные машины',
  'can_create_fire_truck_waybills': 'Может создавать путевые листы пожарных машин',
  'can_delete_fire_truck_waybills': 'Может удалять путевые листы пожарных машин',
  'can_update_fire_truck_waybills': 'Может обновлять путевые листы пожарных машин',
  'can_download_fire_truck_waybills': 'Может скачивать путевые листы пожарных машин',
  'view_fire_truck_waybills': 'Может просматривать путевые листы пожарных машин',
  'can_create_fire_truck_waybills_record': 'Может создавать записи путевых листов пожарных машин',
  'can_delete_fire_truck_waybills_record': 'Может удалять записи путевых листов пожарных машин',
  'can_update_fire_truck_waybills_record': 'Может обновлять записи путевых листов пожарных машин',
  'can_create_fire_truck_norms': 'Может создавать нормы пожарных машин',
  'can_delete_fire_truck_norms': 'Может удалять нормы пожарных машин',
  'can_update_fire_truck_norms': 'Может обновлять нормы пожарных машин',
  'view_fire_truck_norms': 'Может просматривать нормы пожарных машин',
  'can_download_fire_truck_reports': 'Может скачивать отчеты пожарных машин',
  'view_fire_truck_reports': 'Может просматривать отчеты пожарных машин',
  'can_create_passenger_cars': 'Может создавать легковые машины',
  'can_delete_passenger_cars': 'Может удалять легковые машины',
  'can_update_passenger_cars': 'Может обновлять легковые машины',
  'view_passenger_cars': 'Может просматривать легковые машины',
  'can_create_passenger_cars_waybills': 'Может создавать путевые листы легковых машин',
  'can_delete_passenger_cars_waybills': 'Может удалять путевые листы легковых машин',
  'can_update_passenger_cars_waybills': 'Может обновлять путевые листы легковых машин',
  'can_download_passenger_cars_waybills': 'Может скачивать путевые листы легковых машин',
  'view_passenger_cars_waybills': 'Может просматривать путевые листы легковых машин',
  'can_create_passenger_cars_waybills_record': 'Может создавать записи путевых листов легковых машин',
  'can_delete_passenger_cars_waybills_record': 'Может удалять записи путевых листов легковых машин',
  'can_update_passenger_cars_waybills_record': 'Может обновлять записи путевых листов легковых машин',
  'can_create_passenger_cars_norms': 'Может создавать нормы легковых машин',
  'can_delete_passenger_cars_norms': 'Может удалять нормы легковых машин',
  'can_update_passenger_cars_norms': 'Может обновлять нормы легковых машин',
  'view_passenger_cars_norms': 'Может просматривать нормы легковых машин',
  'can_download_passenger_cars_reports': 'Может скачивать отчеты легковых машин',
  'view_passenger_cars_reports': 'Может просматривать отчеты легковых машин',
};
const permissionGroups = {
  users: {
    label: 'Пользователи',
    keys: ['can_create_users', 'can_delete_users', 'can_update_users', 'view_users', 'view_drivers']
  },
  roles: {
    label: 'Роли',
    keys: ['can_create_roles', 'can_delete_roles', 'can_update_roles', 'can_view_roles']
  },
  permissions: {
    label: 'Разрешения',
    keys: ['can_create_permissions', 'can_delete_permissisons', 'can_update_permissisons', 'can_view_permissisons']
  },
  mobile: {
    label: 'Мобильное приложение',
    keys: ['can_use_mobile_booking']
  },
  fire_trucks: {
    label: 'Пожарные машины',
    keys: ['can_create_fire_trucks', 'can_delete_fire_trucks', 'can_update_fire_trucks', 'view_fire_trucks']
  },
  fire_truck_waybills: {
    label: 'Путевые листы пожарных машин',
    keys: ['can_create_fire_truck_waybills', 'can_delete_fire_truck_waybills', 'can_update_fire_truck_waybills', 'can_download_fire_truck_waybills', 'view_fire_truck_waybills']
  },
  fire_truck_waybill_records: {
    label: 'Записи путевых листов пожарных машин',
    keys: ['can_create_fire_truck_waybills_record', 'can_delete_fire_truck_waybills_record', 'can_update_fire_truck_waybills_record']
  },
  fire_truck_norms: {
    label: 'Нормы пожарных машин',
    keys: ['can_create_fire_truck_norms', 'can_delete_fire_truck_norms', 'can_update_fire_truck_norms', 'view_fire_truck_norms']
  },
  fire_truck_reports: {
    label: 'Отчеты пожарных машин',
    keys: ['can_download_fire_truck_reports', 'view_fire_truck_reports']
  },
  passenger_cars: {
    label: 'Легковые машины',
    keys: ['can_create_passenger_cars', 'can_delete_passenger_cars', 'can_update_passenger_cars', 'view_passenger_cars']
  },
  passenger_cars_waybills: {
    label: 'Путевые листы легковых машин',
    keys: ['can_create_passenger_cars_waybills', 'can_delete_passenger_cars_waybills', 'can_update_passenger_cars_waybills', 'can_download_passenger_cars_waybills', 'view_passenger_cars_waybills']
  },
  passenger_cars_waybill_records: {
    label: 'Записи путевых листов легковых машин',
    keys: ['can_create_passenger_cars_waybills_record', 'can_delete_passenger_cars_waybills_record', 'can_update_passenger_cars_waybills_record']
  },
  passenger_cars_norms: {
    label: 'Нормы легковых машин',
    keys: ['can_create_passenger_cars_norms', 'can_delete_passenger_cars_norms', 'can_update_passenger_cars_norms', 'view_passenger_cars_norms']
  },
  passenger_cars_reports: {
    label: 'Отчеты легковых машин',
    keys: ['can_download_passenger_cars_reports', 'view_passenger_cars_reports']
  },
};

const permissionGroupOptions = computed(() => {
  return [
    { value: 'all', label: 'Все' },
    ...Object.entries(permissionGroups).map(([key, group]) => ({
      value: key,
      label: group.label
    }))
  ];
});

const filteredPermissionFields = computed(() => {
  let fields = permissionFields.value;
  if (selectedPermissionGroup.value !== 'all') {
    const groupKeys = permissionGroups[selectedPermissionGroup.value]?.keys || [];
    fields = fields.filter(field => groupKeys.includes(field));
  }
  if (permissionSearchQuery.value) {
    const query = permissionSearchQuery.value.toLowerCase();
    fields = fields.filter(field => {
      const label = permissionsMap[field]?.toLowerCase() || '';
      return label.includes(query);
    });
  }
  return fields;
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
  if (!newRole.value.name) {
    alert('Пожалуйста, введите название роли!');
    return;
  }
  try {
    // 1. Создаём роль
    const roleResp = await axios.post('/roles/', newRole.value, { headers: { Authorization: `Bearer ${auth.access}` } });
    const createdRole = roleResp.data;
    roles.value.push(createdRole);

    // 2. Создаём Permission для этой роли (все поля false)
    const permissionPayload = { role: createdRole.id };
    // Можно добавить сюда дефолтные значения для всех разрешений, если нужно
    const permResp = await axios.post('/permissions/', permissionPayload, { headers: { Authorization: `Bearer ${auth.access}` } });
    // 3. Открываем окно редактирования разрешений для новой роли
    editingRole.value = createdRole;
    // Загружаем разрешения для новой роли
    await loadPermissionsForRole(createdRole.id);
    showAddModal.value = false;
    showEditModal.value = true;
    // Сброс формы
    newRole.value = { name: '' };
  } catch (error) {
    alert('Ошибка при создании роли или разрешений: ' + (error.response?.data?.detail || error.message));
    console.error('Ошибка при создании роли или разрешений:', error);
  }
};

const openEditModal = async (role) => {
  originalRole.value = { ...role };
  editingRole.value = { ...role };
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
  await loadPermissionsForRole(role.id);
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingRole.value = null;
  originalRole.value = null;
  rolePermissions.value = {};
  originalRolePermissions.value = {};
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
};

const hasRoleChanged = () => {
  if (!editingRole.value || !originalRole.value) return false;
  // Проверяем изменение названия роли
  const roleChanged = JSON.stringify(editingRole.value) !== JSON.stringify(originalRole.value);
  // Проверяем изменение разрешений только если есть право их обновлять
  let permissionsChanged = false;
  if (auth.permissions.can_update_permissisons) {
    permissionsChanged = JSON.stringify(rolePermissions.value) !== JSON.stringify(originalRolePermissions.value);
  }
  return roleChanged || permissionsChanged;
};

const loadPermissionsForRole = async (roleId) => {
  // Загружаем разрешения только если есть право на их просмотр и обновление
   if (!auth.permissions.can_view_permissisons || !auth.permissions.can_update_permissisons) {
    return;
  }
  try {
    const url = `/permissions/?role=${roleId}`;
    const response = await axios.get(url, { headers: { Authorization: `Bearer ${auth.access}` } });
    if (response.data && response.data.length > 0) {
      const permission = response.data[0];
      rolePermissions.value = { ...permission };
      originalRolePermissions.value = { ...permission };
      permissionFields.value = Object.keys(permission).filter(
        key => typeof permission[key] === 'boolean' && key !== 'deleted_at'
      );
    }
  } catch (error) {
    console.error('Ошибка при загрузке пермишнов:', error);
  }
};

const formatPermissionLabel = (fieldName) => {
  return permissionsMap[fieldName] || fieldName;
};

const updateRolePermission = (key, value) => {
  rolePermissions.value[key] = value;
};

const updateRole = async () => {
  if (!auth.permissions.can_update_roles) {
    console.warn('Нет разрешения на редактирование ролей.');
    return;
  }
  if (!editingRole.value) return;

  // Проверяем, изменилась ли роль
  if (!hasRoleChanged()) {
    console.log('[Roles] No changes detected');
    closeEditModal();
    return;
  }

  if (!editingRole.value.name) {
    alert('Пожалуйста, заполните название роли!');
    return;
  }
  try {
    const response = await axios.put(`/roles/${editingRole.value.id}/`, editingRole.value, { headers: { Authorization: `Bearer ${auth.access}` } });
    // Обновляем пермишны только если они изменились и есть право на их обновление
    if (auth.permissions.can_update_permissisons && 
        JSON.stringify(rolePermissions.value) !== JSON.stringify(originalRolePermissions.value)) {
      const permResponse = await axios.get(`/permissions/?role=${editingRole.value.id}`, { headers: { Authorization: `Bearer ${auth.access}` } });
      if (permResponse.data && permResponse.data.length > 0) {
        const permissionId = permResponse.data[0].id;
        await axios.put(`/permissions/${permissionId}/`, rolePermissions.value, { headers: { Authorization: `Bearer ${auth.access}` } });
      }
    }
    // Обновляем роль в таблице
    const roleIndex = roles.value.findIndex(r => r.id === editingRole.value.id);
    if (roleIndex > -1) {
      roles.value[roleIndex] = response.data;
    }
    closeEditModal();
  } catch (error) {
    alert('Ошибка при обновлении роли: ' + (error.response?.data?.detail || error.message));
  }
};

const updateRoleAndContinue = async () => {
  if (!auth.permissions.can_update_roles) {
    console.warn('Нет разрешения на редактирование ролей.');
    return;
  }
  if (!editingRole.value) return;

  // Проверяем, изменилась ли роль
  if (!hasRoleChanged()) {
    console.log('[Roles] No changes detected');
    return;
  }

  if (!editingRole.value.name) {
    alert('Пожалуйста, заполните название роли!');
    return;
  }
  try {
    const response = await axios.put(`/roles/${editingRole.value.id}/`, editingRole.value, { headers: { Authorization: `Bearer ${auth.access}` } });
    // Обновляем пермишны только если они изменились и есть право на их обновление
    if (auth.permissions.can_update_permissisons && 
        JSON.stringify(rolePermissions.value) !== JSON.stringify(originalRolePermissions.value)) {
      const permResponse = await axios.get(`/permissions/?role=${editingRole.value.id}`, { headers: { Authorization: `Bearer ${auth.access}` } });
      if (permResponse.data && permResponse.data.length > 0) {
        const permissionId = permResponse.data[0].id;
        await axios.put(`/permissions/${permissionId}/`, rolePermissions.value, { headers: { Authorization: `Bearer ${auth.access}` } });
      }
    }
    // Обновляем роль в таблице
    const roleIndex = roles.value.findIndex(r => r.id === editingRole.value.id);
    if (roleIndex > -1) {
      roles.value[roleIndex] = response.data;
    }
    // Перезагружаем разрешения для продолжения редактирования
    await loadPermissionsForRole(editingRole.value.id);
  } catch (error) {
    alert('Ошибка при обновлении роли: ' + (error.response?.data?.detail || error.message));
  }
};

const onRowClick = (role) => {
  // Проверка прав доступа
  const canUpdateRoles = auth.permissions.can_update_roles;
  const canViewPermissions = auth.permissions.can_view_permissisons;

  // Если нет прав на обновление ролей и не может просматривать разрешения
  if (!canUpdateRoles && !canViewPermissions) {
    // Определяем какое право требуется
    const requiredPermission = 'can_update_roles';
    permissionDeniedModal.value?.openModal(requiredPermission);
    return;
  }

  openEditModal(role);
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
    console.warn('Нет разрешения на удаление ролей.');
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

const handleCrudDelete = () => {
  openDeleteModal();
};

onMounted(() => {
   setupCrudPermissions();
    console.log("[Roles] User permissions:", auth.permissions); 
   if (auth.permissions.can_view_roles) {
     fetchRoles();
  } else {
    console.warn("[Roles] User does not have permission to view roles.");
  }
  // Загружаем пользователей если есть право на просмотр
  fetchUsers();
  window.addEventListener('crud:create', handleCrudCreate);
  window.addEventListener('crud:delete', handleCrudDelete);
 });


onUnmounted(() => {
  auth.clearCrudPermissions();
  
  window.removeEventListener('crud:create', handleCrudCreate);
  window.removeEventListener('crud:delete', handleCrudDelete);
}); 
</script>
