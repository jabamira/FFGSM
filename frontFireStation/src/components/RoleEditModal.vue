<template>
  <ErrorModal ref="errorModalRef" />
  
  <Modal
    :is-open="isOpen"
    title="Редактировать роль"
    @close="closeModal"
  >
    <div v-if="editingRole" class="space-y-4 min-w-96">
      <!-- Поле для редактирования названия роли -->
      <div>
        <TextInput 
          v-model="editingRole.name" 
          :label="fieldDefinitions.role.name.label" 
          :hint="fieldDefinitions.role.name.hint"
          placeholder="Введите название роли"
          :disabled="!auth.permissions.can_update_roles"
          :required="fieldDefinitions.role.name.required"
        />
      </div>
      
      <!-- Раздел разрешений (пермишны) - видимо только если есть право на просмотр разрешений -->
      <div v-if="auth.permissions.can_view_permissisons && auth.permissions.can_update_permissisons" class="border-t pt-4">
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

    <!-- Permission Denied Message -->
    <div v-if="!auth.permissions.can_update_roles" class="rounded p-4 bg-yellow-50 border border-yellow-200">
      <p class="text-sm text-yellow-800">
        У вас нет прав на редактирование ролей. Данные доступны только для просмотра.
      </p>
    </div>

    <template #footer>
      <Button variant="secondary" size="md" @click="closeModal">Закрыть</Button>
      <Button 
        v-if="auth.permissions.can_update_roles"
        variant="primary" 
        size="md" 
        @click="updateRole"
        :disabled="!hasRoleChanged()"
      >
        Сохранить
      </Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, TextInput, SelectInput, palette } from './ui/importUi';
import ErrorModal from './ErrorModal.vue';
import { useAuthStore } from '../stores/auth';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields, createValidationError } from '../utils/errorUtils';
import axios from 'axios';

const auth = useAuthStore();
const errorModalRef = ref(null);
const isOpen = ref(false);
const editingRole = ref(null);
const originalRole = ref(null);
const rolePermissions = ref({});
const originalRolePermissions = ref({});
const permissionFields = ref([]);
const permissionSearchQuery = ref('');
const selectedPermissionGroup = ref('all');

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
  'can_download_drivers_reports': 'Может скачивать отчеты водителей',
  'view_drivers_reports': 'Может просматривать отчеты водителей',
  'can_create_technical_maintenance': 'Может создавать техническое обслуживание',
  'can_delete_technical_maintenance': 'Может удалять техническое обслуживание',
  'can_update_technical_maintenance': 'Может обновлять техническое обслуживание',
  'view_technical_maintenance': 'Может просматривать техническое обслуживание',
  'can_view_operating_hours': 'Может просматривать рабочие часы',
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
    keys: ['can_create_fire_truck_waybills_records', 'can_delete_fire_truck_waybills_records','view_fire_truck_waybills_records', 'can_update_fire_truck_waybills_records']
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
    keys: ['can_create_passenger_cars_waybills_records', 'can_delete_passenger_cars_waybills_records', 'can_update_passenger_cars_waybills_records', 'view_passenger_cars_waybills_records']
  },
  passenger_cars_norms: {
    label: 'Нормы легковых машин',
    keys: ['can_create_passenger_cars_norms', 'can_delete_passenger_cars_norms', 'can_update_passenger_cars_norms', 'view_passenger_cars_norms']
  },
  passenger_cars_reports: {
    label: 'Отчеты легковых машин',
    keys: ['can_download_passenger_cars_reports', 'view_passenger_cars_reports']
  },
  drivers: {
    label: 'Водители',
    keys: ['view_drivers', 'can_download_drivers_reports', 'view_drivers_reports']
  },
  technical_maintenance: {
    label: 'Техническое обслуживание',
    keys: ['can_create_technical_maintenance', 'can_delete_technical_maintenance', 'can_update_technical_maintenance', 'view_technical_maintenance']
  },
  operating_hours: {
    label: 'Рабочие часы',
    keys: ['can_view_operating_hours']
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

const formatPermissionLabel = (fieldName) => {
  return permissionsMap[fieldName] || fieldName;
};

const updateRolePermission = (key, value) => {
  rolePermissions.value[key] = value;
};

const hasRoleChanged = () => {
  if (!editingRole.value || !originalRole.value) return false;
  const roleChanged = JSON.stringify(editingRole.value) !== JSON.stringify(originalRole.value);
  let permissionsChanged = false;
  if (auth.permissions.can_update_permissisons) {
    permissionsChanged = JSON.stringify(rolePermissions.value) !== JSON.stringify(originalRolePermissions.value);
  }
  return roleChanged || permissionsChanged;
};

const loadPermissionsForRole = async (roleId) => {
  if (!auth.permissions.can_view_permissisons && !auth.permissions.can_update_permissisons) {
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

const openModal = async (role) => {
  originalRole.value = { ...role };
  editingRole.value = { ...role };
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
  await loadPermissionsForRole(role.id);
  isOpen.value = true;
};

const closeModal = () => {
  isOpen.value = false;
  editingRole.value = null;
  originalRole.value = null;
  rolePermissions.value = {};
  originalRolePermissions.value = {};
  permissionSearchQuery.value = '';
  selectedPermissionGroup.value = 'all';
};

const updateRole = async () => {
  if (!auth.permissions.can_update_roles) {
    console.warn('Нет разрешения на редактирование ролей.');
    return;
  }
  if (!editingRole.value) return;

  if (!hasRoleChanged()) {
    console.log('[RoleEditModal] No changes detected');
    closeModal();
    return;
  }

  // Validate all role fields
  const validationErrors = validateFormFields(editingRole.value, fieldDefinitions.role);
  if (Object.keys(validationErrors).length > 0) {
    const error = createValidationError(validationErrors, 'Пожалуйста, проверьте заполненные поля');
    errorModalRef.value?.openModal(error);
    return;
  }

  // Проверка разрешения перед отправкой
  if (!auth.permissions.can_update_roles) {
    errorModalRef.value?.openModal({
      response: {
        data: {
          detail: 'У вас нет прав на редактирование ролей'
        }
      }
    });
    return;
  }

  try {
    const response = await axios.put(`/roles/${editingRole.value.id}/`, editingRole.value, { headers: { Authorization: `Bearer ${auth.access}` } });
    if (auth.permissions.can_update_permissisons && 
        JSON.stringify(rolePermissions.value) !== JSON.stringify(originalRolePermissions.value)) {
      const permResponse = await axios.get(`/permissions/?role=${editingRole.value.id}`, { headers: { Authorization: `Bearer ${auth.access}` } });
      if (permResponse.data && permResponse.data.length > 0) {
        const permissionId = permResponse.data[0].id;
        await axios.put(`/permissions/${permissionId}/`, rolePermissions.value, { headers: { Authorization: `Bearer ${auth.access}` } });
      }
    }
    emit('role-updated', response.data);
    closeModal();
  } catch (error) {
    console.error('Ошибка при обновлении роли:', error);
    errorModalRef.value?.openModal(error);
  }
};

const emit = defineEmits(['role-updated']);

defineExpose({
  openModal,
  closeModal
});
</script>
