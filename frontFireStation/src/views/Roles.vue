
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
  
    <div class="p-6 max-w-6xl mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Роли</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <DataTable 
          :data="filteredRoles" 
          :columns="columns"
          :selectable="true"
          :show-select-all="false"
          :selected-rows="getSelectedIndexes()"
          @row-selected="onRowsSelected"
          @row-click="onRowClick"
        />
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

    <!-- Modal редактирования разрешений роли -->
    <Modal
      :is-open="showEditModal"
      title="Редактировать разрешения роли"
      @close="closeEditModal"
    >
      <div v-if="editingRole" class="space-y-4 min-w-96">
        <div class="font-semibold mb-2">{{ editingRole.name }}</div>
        <!-- Раздел разрешений (пермишны) -->
        <div class="border-t pt-4">
          <p :style="{ color: palette.dark }" class="font-semibold mb-4">Разрешения</p>
          <div class="space-y-3 mb-4">
            <SelectInput 
              v-model="selectedPermissionGroup" 
              label="Группа" 
              :options="permissionGroupOptions"
              placeholder="Выберите группу"
            />
            <TextInput 
              v-model="permissionSearchQuery" 
              label="Поиск" 
              placeholder="Введите название разрешения"
            />
          </div>
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <label v-for="field in filteredPermissionFields" :key="field" class="flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                :checked="rolePermissions[field]"
                :disabled="!auth.permissions.can_update_permissisons"
                @change="updateRolePermission(field, $event.target.checked)"
                class="w-4 h-4 rounded mr-2"
              />
              <span :style="{ color: palette.dark }" class="text-sm">{{ formatPermissionLabel(field) }}</span>
            </label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeEditModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="updateRole">Сохранить</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { DataTable, TextInput, palette, Modal, Button, SelectInput } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';

const auth = useAuthStore();
const roles = ref([]);
const searchQuery = ref('');
const selectedRoleIds = ref([]);
const showAddModal = ref(false);
const showEditModal = ref(false);
const editingRole = ref(null);
const rolePermissions = ref({});
const permissionFields = ref([]);
const permissionSearchQuery = ref('');
const selectedPermissionGroup = ref('all');

const columns = [
  { key: 'name', label: 'Название роли' }
];


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

const filteredRoles = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return roles.value.filter(role => role.name.toLowerCase().includes(query));
});

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
    if (!auth.permissions.can_update_roles) {
    console.warn('Нет разрешения на редактирование ролей.');
    return;
  }
  editingRole.value = { ...role };
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
  await loadPermissionsForRole(role.id);
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingRole.value = null;
  rolePermissions.value = {};
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
};

const loadPermissionsForRole = async (roleId) => {
  try {
    const url = `/permissions/?role=${roleId}`;
    const response = await axios.get(url, { headers: { Authorization: `Bearer ${auth.access}` } });
    if (response.data && response.data.length > 0) {
      const permission = response.data[0];
      rolePermissions.value = { ...permission };
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
  if (!editingRole.value.name) {
    alert('Пожалуйста, заполните название роли!');
    return;
  }
  try {
    const response = await axios.put(`/roles/${editingRole.value.id}/`, editingRole.value, { headers: { Authorization: `Bearer ${auth.access}` } });
    // Обновляем пермишны
    if (auth.permissions.can_update_permissisons && Object.keys(rolePermissions.value).length > 0) {
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

const onRowClick = (role) => {
  openEditModal(role);
};

const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_roles || false,
    canDelete: auth.permissions.can_delete_roles || false,
  });
};

const handleCrudCreate = () => {
  openAddModal();
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
  window.addEventListener('crud:create', handleCrudCreate);
  window.addEventListener('crud:delete', handleCrudDelete);
 });


onUnmounted(() => {
  auth.clearCrudPermissions();
  
  window.removeEventListener('crud:create', handleCrudCreate);
  window.removeEventListener('crud:delete', handleCrudDelete);
}); 
</script>
