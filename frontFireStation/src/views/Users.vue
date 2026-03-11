<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Пользователи</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите ФИО, логин или телефон" class="mb-4" />
        <DataTable 
          :data="filteredUsers" 
          :columns="columns"
          :selectable="true"
          :show-select-all="false"
          :selected-rows="getSelectedIndexes()"
          @row-selected="onRowsSelected"
          @row-click="onRowClick"
        >
        </DataTable>
      </div>
    </div>

    <!-- Modal добавления пользователя -->
    <Modal
      :is-open="showAddModal"
      title="Добавить пользователя"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <TextInput 
          v-model="newUser.name" 
          label="Имя" 
          placeholder="Введите имя"
          required
        />
        <TextInput 
          v-model="newUser.surname" 
          label="Фамилия" 
          placeholder="Введите фамилию"
          required
        />
        <TextInput 
          v-model="newUser.last_name" 
          label="Отчество" 
          placeholder="Введите отчество"
          required
        />
        <TextInput 
          v-model="newUser.login" 
          label="Логин" 
          placeholder="Введите логин"
          required
        />
        <TextInput 
          v-model="newUser.password" 
          label="Пароль" 
          placeholder="Введите пароль"
          type="password"
          required
        />
        <TextInput 
          v-model="newUser.phone" 
          label="Телефон" 
          placeholder="Введите телефон"
          required
        />
        <TextInput 
          v-model="newUser.driver_license" 
          label="Водительское удостоверение" 
          placeholder="Введите номер удостоверения (опционально)"
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
          <div class="max-w-6xl mx-auto mt-8 mb-4 text-sm text-gray-500">

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

    <!-- Modal редактирования пользователя -->
    <Modal
      :is-open="showEditModal"
      title="Редактировать пользователя"
      @close="closeEditModal"
    >
      <div v-if="editingUser" class="space-y-4 min-w-96">
        <TextInput 
          v-model="editingUser.name" 
          label="Имя" 
          placeholder="Введите имя"
          required
        />
        <TextInput 
          v-model="editingUser.surname" 
          label="Фамилия" 
          placeholder="Введите фамилию"
          required
        />
        <TextInput 
          v-model="editingUser.last_name" 
          label="Отчество" 
          placeholder="Введите отчество"
          required
        />
        <TextInput 
          v-model="editingUser.login" 
          label="Логин" 
          placeholder="Введите логин"
          required
        />
        <TextInput 
          v-model="editingUser.password" 
          label="Пароль" 
          placeholder="Введите пароль (оставьте пустым, чтобы не менять)"
          type="password"
        />
        <TextInput 
          v-model="editingUser.phone" 
          label="Телефон" 
          placeholder="Введите телефон"
          required
        />
        <TextInput 
          v-model="editingUser.driver_license" 
          label="Водительское удостоверение" 
          placeholder="Введите номер удостоверения (опционально)"
        />

        <SelectInput 
          v-model="editingUser.role" 
          label="Роль" 
          :options="roleOptions"
          required
        />

          <!-- Отображение текущей роли и всех ролей -->
          <div class="mt-2 text-xs text-gray-500">
            <div>
              <span>Текущая роль: </span>
              <span class="font-semibold text-blue-700">
                {{ roles.find(r => r.id === editingUser.role)?.name || 'Не определена' }}
              </span>
            </div>
            <div>
              <span>Доступные роли: </span>
              <span class="font-semibold text-blue-700">
                <template v-if="roles && roles.length">
                  {{ roles.map(r => r.name).join(', ') }}
                </template>
                <template v-else>
                  Нет ролей
                </template>
              </span>
            </div>
          </div>

        <!-- Чекбоксы пермишнов -->
        <!-- ...раздел разрешений удалён, теперь он на странице ролей... -->
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeEditModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="updateUser">Сохранить</Button>
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
const users = ref([]);
const roles = ref([]);
const searchQuery = ref('');
const selectedUserIds = ref([]);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);
const editingUser = ref(null);
const userPermissions = ref({});
const permissionFields = ref([]);
const permissionSearchQuery = ref('');
const selectedPermissionGroup = ref('all');

const columns = [
  { key: 'name', label: 'Имя' },
  { key: 'surname', label: 'Фамилия' },
  { key: 'last_name', label: 'Отчество' },
  { key: 'login', label: 'Логин' },
  { key: 'phone', label: 'Телефон' }
];

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

// Маппинг название пермишнов на русский
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

// Группировка пермишнов
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

const getGroupKeysForPermission = (field) => {
  for (const [groupKey, group] of Object.entries(permissionGroups)) {
    if (group.keys.includes(field)) {
      return groupKey;
    }
  }
  return null;
};

const filteredPermissionFields = computed(() => {
  let fields = permissionFields.value;
  
  // Фильтр по группе
  if (selectedPermissionGroup.value !== 'all') {
    const groupKeys = permissionGroups[selectedPermissionGroup.value]?.keys || [];
    fields = fields.filter(field => groupKeys.includes(field));
  }
  
  // Фильтр по поиску (по русскому названию)
  if (permissionSearchQuery.value) {
    const query = permissionSearchQuery.value.toLowerCase();
    fields = fields.filter(field => {
      const label = permissionsMap[field]?.toLowerCase() || '';
      return label.includes(query);
    });
  }
  
  return fields;
});

const roleOptions = computed(() => {
  return roles.value.map(role => ({
    value: role.id,
    label: role.name
  }));
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
    users.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке пользователей:', error);
  }
};


const filteredUsers = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return users.value.filter(user =>
    user.name.toLowerCase().includes(query) ||
    user.surname.toLowerCase().includes(query) ||
    user.last_name.toLowerCase().includes(query) ||
    user.login.toLowerCase().includes(query) ||
    user.phone.includes(query)
  );
});

const usersToDelete = computed(() => {
  return filteredUsers.value.filter(u => selectedUserIds.value.includes(u.id));
});

const getSelectedIndexes = () => {
  return filteredUsers.value
    .map((user, index) => selectedUserIds.value.includes(user.id) ? index : -1)
    .filter(index => index !== -1);
};

const onRowsSelected = (selectedIndexes) => {
  selectedUserIds.value = selectedIndexes.map(idx => filteredUsers.value[idx].id);
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
    role: null,
  };
};

const addUser = async () => {
  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на создание пользователей.');
    return;
  }

  // Валидация полей
  if (!newUser.value.name || !newUser.value.surname || !newUser.value.last_name || 
      !newUser.value.login || !newUser.value.password || !newUser.value.phone) {
    console.warn('Все основные поля обязательны для заполнения.');
    alert('Пожалуйста, заполните все основные поля!');
    return;
  }

  try {
    const response = await axios.post('/users/', newUser.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[Users] User added successfully:', response.data);
    users.value.push(response.data);
    closeAddModal();
  } catch (error) {
    console.error('Ошибка при добавлении пользователя:', error);
    alert('Ошибка при добавлении пользователя: ' + (error.response?.data?.detail || error.message));
  }
};

const openEditModal = async (user) => {
  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на редактирование пользователей.');
    return;
  }
  
  editingUser.value = { ...user, password: '' };
  
  // Очищаем фильтры пермишнов
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
  
  // Загружаем пермишны для роли пользователя
  await loadPermissionsForRole(user.role);
  
  // Вывод в консоль для отладки
  console.log('[Users] Editing user:', user);
  console.log('[Users] User role:', user.role);
  console.log('[Users] User permissions:', userPermissions.value);
  
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingUser.value = null;
  userPermissions.value = {};
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
};

const loadPermissionsForRole = async (roleId) => {
  try {
    const url = `/permissions/?role=${roleId}`;
    console.log('[Users] Loading permissions for role:', roleId, 'URL:', url);
    
    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[Users] API Response:', response.data);
    
    if (response.data && response.data.length > 0) {
      const permission = response.data[0];
      
      // Проверяем что пермишны действительно для нужной роли
      if (permission.role !== roleId) {
        console.warn(`[Users] WARNING: Requested permissions for role ${roleId}, but got role ${permission.role}!`);
      }
      
      userPermissions.value = { ...permission };
      
      // Извлекаем все поля пермишнов (boolean поля)
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

const updateUserPermission = (key, value) => {
  userPermissions.value[key] = value;
};

const updateUser = async () => {
  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на редактирование пользователей.');
    return;
  }

  if (!editingUser.value) return;

  // Валидация полей
  if (!editingUser.value.name || !editingUser.value.surname || !editingUser.value.last_name || 
      !editingUser.value.login || !editingUser.value.phone) {
    console.warn('Все основные поля обязательны для заполнения.');
    alert('Пожалуйста, заполните все основные поля!');
    return;
  }

  try {
    const updateData = { ...editingUser.value };
    if (!updateData.password) {
      delete updateData.password;
    }

    // Обновляем пользователя
    const response = await axios.put(`/users/${editingUser.value.id}/`, updateData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[Users] User updated successfully:', response.data);
    
    // Обновляем пермишны если они были изменены и пользователь имеет разрешение
    if (auth.permissions.can_update_permissisons && Object.keys(userPermissions.value).length > 0) {
      // Находим Permission для роли пользователя
      const permResponse = await axios.get(`/permissions/?role=${editingUser.value.role}`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
      
      if (permResponse.data && permResponse.data.length > 0) {
        const permissionId = permResponse.data[0].id;
        
        // Обновляем пермишны
        await axios.put(`/permissions/${permissionId}/`, userPermissions.value, {
          headers: { Authorization: `Bearer ${auth.access}` }
        });
        
        console.log('[Users] Permissions updated successfully');
      }
    }
    
    // Обновляем пользователя в таблице
    const userIndex = users.value.findIndex(u => u.id === editingUser.value.id);
    if (userIndex > -1) {
      users.value[userIndex] = response.data;
    }
    
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при обновлении пользователя:', error);
    alert('Ошибка при обновлении пользователя: ' + (error.response?.data?.detail || error.message));
  }
};

const onRowClick = (user) => {
  openEditModal(user);
};

const openDeleteModal = () => {
  if (selectedUserIds.value.length === 0) {
    console.warn('Не выбраны пользователи для удаления.');
    return;
  }
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const confirmDelete = async () => {
  if (!auth.permissions.can_delete_users) {
    console.warn('Нет разрешения на удаление пользователей.');
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

// Следим за изменением роли в режиме редактирования
watch(
  () => editingUser.value?.role,
  async (newRole) => {
    if (newRole && editingUser.value) {
      await loadPermissionsForRole(newRole);
      console.log('[Users] Role changed to:', newRole);
      console.log('[Users] New permissions loaded:', userPermissions.value);
    }
  }
);

onMounted(() => {
  console.debug("[Users] Permissions loaded from store:", auth.permissions);
  setupCrudPermissions();
  
  fetchRoles();
  
  if (auth.permissions.view_users) {
    fetchUsers();
  } else {
    console.warn("[Users] User does not have permission to view users.");
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
