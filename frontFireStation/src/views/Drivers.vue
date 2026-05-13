<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Водители</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите ФИО, телефон или удостоверение" class="mb-4" />
        <DataTable 
          :data="filteredDrivers" 
          :columns="columns"
          :selectable="true"
          :show-select-all="false"
          :selected-rows="selectedDriverIds"
          @row-selected="onRowsSelected"
          @row-click="onRowClick"
          row-id-key="id"
        >
        </DataTable>
      </div>
    </div>

    <!-- Modal добавления водителя -->
    <Modal
      :is-open="showAddModal"
      title="Создать водителя"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <div v-if="addFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ addFormGeneralError }}</p>
        </div>
        <TextInput 
          v-model="newDriver.name" 
          :label="fieldDefinitions.driverCreate.name.label" 
          :hint="fieldDefinitions.driverCreate.name.hint"
          :error="addFormErrors.name"
          placeholder="Введите имя"
          :required="fieldDefinitions.driverCreate.name.required"
        />
        <TextInput 
          v-model="newDriver.surname" 
          :label="fieldDefinitions.driverCreate.surname.label" 
          :hint="fieldDefinitions.driverCreate.surname.hint"
          :error="addFormErrors.surname"
          placeholder="Введите фамилию"
          :required="fieldDefinitions.driverCreate.surname.required"
        />
        <TextInput 
          v-model="newDriver.last_name" 
          :label="fieldDefinitions.driverCreate.last_name.label" 
          :hint="fieldDefinitions.driverCreate.last_name.hint"
          :error="addFormErrors.last_name"
          placeholder="Введите отчество"
          :required="fieldDefinitions.driverCreate.last_name.required"
        />
        <TextInput 
          v-model="newDriver.login" 
          :label="fieldDefinitions.driverCreate.login.label" 
          :hint="fieldDefinitions.driverCreate.login.hint"
          :error="addFormErrors.login"
          placeholder="Введите логин"
          :required="fieldDefinitions.driverCreate.login.required"
        />
        <TextInput 
          v-model="newDriver.password" 
          :label="fieldDefinitions.driverCreate.password.label" 
          :hint="fieldDefinitions.driverCreate.password.hint"
          :error="addFormErrors.password"
          placeholder="Введите пароль"
          type="password"
          :required="fieldDefinitions.driverCreate.password.required"
        />
        <TextInput 
          v-model="newDriver.phone" 
          :label="fieldDefinitions.driverCreate.phone.label" 
          :hint="fieldDefinitions.driverCreate.phone.hint"
          :error="addFormErrors.phone"
          placeholder="Введите телефон"
          :required="fieldDefinitions.driverCreate.phone.required"
        />
        <TextInput 
          v-model="newDriver.driver_license" 
          :label="fieldDefinitions.driverCreate.driver_license.label" 
          :hint="fieldDefinitions.driverCreate.driver_license.hint"
          :error="addFormErrors.driver_license"
          placeholder="Введите номер удостоверения"
          :required="fieldDefinitions.driverCreate.driver_license.required"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeAddModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="addDriver">Добавить</Button>
      </template>
    </Modal>

    <!-- Modal подтверждения удаления -->
    <Modal
      :is-open="showDeleteModal"
      title="Подтвердить удаление"
      @close="closeDeleteModal"
    >
      <div class="space-y-4">
        <p :style="{ color: palette.dark }">Вы уверены что хотите удалить следующих водителей:</p>
        <div class="bg-red-50 border border-red-200 rounded p-4">
          <ul class="space-y-2">
            <li v-for="driver in driversToDelete" :key="driver.id" :style="{ color: palette.dark }">
              {{ driver.surname }} {{ driver.name }} {{ driver.last_name }}
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeDeleteModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="confirmDelete">Удалить</Button>
      </template>
    </Modal>

    <!-- Modal редактирования водителя -->
    <Modal
      :is-open="showEditModal"
      title="Редактировать водителя"
      @close="closeEditModal"
    >
      <div v-if="editingDriver" class="space-y-4 min-w-96">
        <div v-if="editFormGeneralError" class="rounded-lg p-4 bg-red-50 border-l-4 border-red-500">
          <p class="text-sm font-semibold text-red-600">{{ editFormGeneralError }}</p>
        </div>
        <TextInput 
          v-model="editingDriver.name" 
          :label="fieldDefinitions.driverEdit.name.label" 
          :hint="fieldDefinitions.driverEdit.name.hint"
          :error="editFormErrors.name"
          placeholder="Введите имя"
          :required="fieldDefinitions.driverEdit.name.required"
        />
        <TextInput 
          v-model="editingDriver.surname" 
          :label="fieldDefinitions.driverEdit.surname.label" 
          :hint="fieldDefinitions.driverEdit.surname.hint"
          :error="editFormErrors.surname"
          placeholder="Введите фамилию"
          :required="fieldDefinitions.driverEdit.surname.required"
        />
        <TextInput 
          v-model="editingDriver.last_name" 
          :label="fieldDefinitions.driverEdit.last_name.label" 
          :hint="fieldDefinitions.driverEdit.last_name.hint"
          :error="editFormErrors.last_name"
          placeholder="Введите отчество"
          :required="fieldDefinitions.driverEdit.last_name.required"
        />
        <TextInput 
          v-model="editingDriver.login" 
          :label="fieldDefinitions.driverEdit.login.label" 
          :hint="fieldDefinitions.driverEdit.login.hint"
          :error="editFormErrors.login"
          placeholder="Введите логин"
          :required="fieldDefinitions.driverEdit.login.required"
        />
        <TextInput 
          v-model="editingDriver.password" 
          :label="fieldDefinitions.driverEdit.password.label" 
          :hint="fieldDefinitions.driverEdit.password.hint"
          :error="editFormErrors.password"
          placeholder="Введите пароль (оставьте пустым, чтобы не менять)"
          type="password"
          :required="fieldDefinitions.driverEdit.password.required"
        />
        <TextInput 
          v-model="editingDriver.phone" 
          :label="fieldDefinitions.driverEdit.phone.label" 
          :hint="fieldDefinitions.driverEdit.phone.hint"
          :error="editFormErrors.phone"
          placeholder="Введите телефон"
          :required="fieldDefinitions.driverEdit.phone.required"
        />
        <TextInput 
          v-model="editingDriver.driver_license" 
          :label="fieldDefinitions.driverEdit.driver_license.label" 
          :hint="fieldDefinitions.driverEdit.driver_license.hint"
          :error="editFormErrors.driver_license"
          placeholder="Введите номер удостоверения"
          :required="fieldDefinitions.driverEdit.driver_license.required"
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeEditModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="updateDriver" :disabled="!hasDriverChanged()">Сохранить</Button>
      </template>
    </Modal>

    <!-- Permission Denied Modal -->
    <PermissionDeniedModal ref="permissionDeniedModal" />

    <!-- No Selection Modal -->
    <NoSelectionModal ref="noSelectionModal" />

    <!-- Error Modal -->
    <ErrorModal ref="errorModalRef" />

    <!-- CRUD Panel -->
    <CrudPanel 
      @create="handleCrudCreate"
      @delete="handleCrudDelete"
      createLabel="Создать водителя"
      :deleteLabel="deleteButtonLabel"
      :isDeleteDisabled="isDeleteDisabled"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { DataTable, TextInput, palette, Modal, Button } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import { useSearch } from '../composables/useSearch';
import { fieldDefinitions } from '../config/fieldDefinitions';
import { validateFormFields, createValidationError } from '../utils/errorUtils';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';
import PermissionDeniedModal from '../components/PermissionDeniedModal.vue';
import NoSelectionModal from '../components/NoSelectionModal.vue';
import CrudPanel from '../components/CrudPanel.vue';
import ErrorModal from '../components/ErrorModal.vue';

const auth = useAuthStore();
const drivers = ref([]);
const selectedDriverIds = ref([]);
const permissionDeniedModal = ref(null);
const noSelectionModal = ref(null);
const errorModalRef = ref(null);
const { searchQuery, filtered: filteredDrivers } = useSearch(drivers, ['name', 'surname', 'last_name', 'phone', 'driver_license']);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);
const editingDriver = ref(null);
const originalDriver = ref(null);

const columns = [
  { key: 'name', label: 'Имя' },
  { key: 'surname', label: 'Фамилия' },
  { key: 'last_name', label: 'Отчество' },
  { key: 'phone', label: 'Телефон' },
  { key: 'driver_license', label: 'Водительское удостоверение' }
];

const newDriver = ref({
  name: '',
  surname: '',
  last_name: '',
  login: '',
  password: '',
  phone: '',
  driver_license: '',
  role: 3,
});

const addFormErrors = ref({});
const editFormErrors = ref({});
const addFormGeneralError = ref('');
const editFormGeneralError = ref('');

const fetchDrivers = async () => {
  // Проверяем разрешение view_drivers
  if (!auth.permissions.view_drivers) {
    console.warn('Нет разрешения на просмотр водителей (view_drivers).');
    return;
  }

  try {
    // Используем специальный endpoint /users/drivers/ для получения только водителей
    const response = await axios.get('/users/drivers/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    drivers.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке водителей:', error);
  }
};

const driversToDelete = computed(() => {
  return filteredDrivers.value.filter(d => selectedDriverIds.value.includes(d.id));
});

const onRowsSelected = (selectedIds) => {
  selectedDriverIds.value = selectedIds;
};

const openAddModal = () => {
  resetNewDriver();
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  resetNewDriver();
  addFormErrors.value = {};
  addFormGeneralError.value = '';
};

const resetNewDriver = () => {
  newDriver.value = {
    name: '',
    surname: '',
    last_name: '',
    login: '',
    password: '',
    phone: '',
    driver_license: '',
    role: 3,
  };
};

const addDriver = async () => {
  addFormGeneralError.value = '';
  addFormErrors.value = {};

  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на создание водителей.');
    return;
  }

  // Валидация полей на клиенте
  const validationErrors = validateFormFields(newDriver.value, fieldDefinitions.driverCreate);
  if (Object.keys(validationErrors).length > 0) {
    addFormErrors.value = validationErrors;
    addFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  try {
    // Отправляем запрос на создание пользователя
    const response = await axios.post('/users/', newDriver.value, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[Drivers] Driver added successfully:', response.data);
    
    // Добавляем нового водителя в таблицу без перезагрузки
    drivers.value.push(response.data);
    
    // Закрываем модальное окно
    closeAddModal();
  } catch (error) {
    console.error('Ошибка при добавлении водителя:', error);
    errorModalRef.value?.openModal(error);
  }
};

const onRowClick = (driver) => {
  // Проверка прав доступа
  const canUpdateUsers = auth.permissions.can_update_users;

  // Если нет прав на обновление пользователей
  if (!canUpdateUsers) {
    permissionDeniedModal.value?.openModal('can_update_users');
    return;
  }

  openEditModal(driver);
};

const openEditModal = (driver) => {
  // Сохраняем оригинальные данные водителя
  originalDriver.value = { ...driver, password: '' };
  editingDriver.value = { ...driver, password: '' };
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingDriver.value = null;
  originalDriver.value = null;
  editFormErrors.value = {};
  editFormGeneralError.value = '';
};

const hasDriverChanged = () => {
  if (!editingDriver.value || !originalDriver.value) return false;
  return JSON.stringify(editingDriver.value) !== JSON.stringify(originalDriver.value);
};

const updateDriver = async () => {
  editFormGeneralError.value = '';
  editFormErrors.value = {};

  if (!auth.permissions.can_update_users) {
    console.warn('Нет разрешения на редактирование водителей.');
    return;
  }

  if (!editingDriver.value) return;

  // Проверяем, изменились ли данные
  if (!hasDriverChanged()) {
    console.log('[Drivers] No changes detected');
    closeEditModal();
    return;
  }

  // Валидация полей на клиенте
  const validationErrors = validateFormFields(editingDriver.value, fieldDefinitions.driverEdit);
  if (Object.keys(validationErrors).length > 0) {
    editFormErrors.value = validationErrors;
    editFormGeneralError.value = 'Пожалуйста, проверьте заполненные поля';
    return;
  }

  try {
    const updateData = { ...editingDriver.value };
    // Удаляем пароль если он пустой (не отправляем на сервер)
    if (!updateData.password) {
      delete updateData.password;
    }

    // Отправляем запрос на обновление пользователя
    const response = await axios.put(`/users/${editingDriver.value.id}/`, updateData, {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    
    console.log('[Drivers] Driver updated successfully:', response.data);
    
    // Обновляем водителя в таблице
    const driverIndex = drivers.value.findIndex(d => d.id === editingDriver.value.id);
    if (driverIndex > -1) {
      drivers.value[driverIndex] = response.data;
    }
    
    // Закрываем модальное окно
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при обновлении водителя:', error);
    errorModalRef.value?.openModal(error);
  }
};

const openDeleteModal = () => {
  if (selectedDriverIds.value.length === 0) {
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
    // Удаляем каждого выбранного водителя
    for (const id of selectedDriverIds.value) {
      await axios.delete(`/users/${id}/`, {
        headers: { Authorization: `Bearer ${auth.access}` }
      });
    }
    
    console.log('[Drivers] Drivers deleted successfully');
    
    // Перезагружаем список водителей и очищаем выделение
    selectedDriverIds.value = [];
    await fetchDrivers();
    closeDeleteModal();
  } catch (error) {
    console.error('Ошибка при удалении водителей:', error);
  }
};

/**
 * Установить CRUD разрешения для этой страницы на основе разрешений пользователя
 */
const setupCrudPermissions = () => {
  auth.setCrudPermissions({
    canCreate: auth.permissions.can_create_users || false,
    canDelete: auth.permissions.can_delete_users || false,
  });
};

// Функция для обработки события create из CrudPanel
const handleCrudCreate = () => {
  openAddModal();
};

const deleteButtonLabel = computed(() => {
  const count = selectedDriverIds.value.length;
  if (count === 0) return 'Удалить водителя';
  if (count === 1) return 'Удалить водителя';
  return `Удалить водителей (${count})`;
});

const isDeleteDisabled = computed(() => selectedDriverIds.value.length === 0);

// Функция для обработки события delete из CrudPanel
const handleCrudDelete = () => {
  openDeleteModal();
};

onMounted(() => {
  console.debug("[Drivers] Permissions loaded from store:", auth.permissions);
  setupCrudPermissions();
  
  if (auth.permissions.view_drivers) {
    fetchDrivers();
  } else {
    console.warn("[Drivers] User does not have permission to view drivers.");
    permissionDeniedModal.value?.openModal('view_drivers');
  }
});

onUnmounted(() => {
  // Очистить CRUD разрешения при выходе со страницы
  auth.clearCrudPermissions();
});
</script>
