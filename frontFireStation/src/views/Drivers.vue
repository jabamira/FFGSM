<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Водители</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите ФИО, телефон или удостоверение" class="mb-4" />
        <DataTable 
          :data="filteredDrivers" 
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

    <!-- Modal добавления водителя -->
    <Modal
      :is-open="showAddModal"
      title="Добавить водителя"
      @close="closeAddModal"
    >
      <div class="space-y-4 min-w-96">
        <TextInput 
          v-model="newDriver.name" 
          label="Имя" 
          placeholder="Введите имя"
          required
        />
        <TextInput 
          v-model="newDriver.surname" 
          label="Фамилия" 
          placeholder="Введите фамилию"
          required
        />
        <TextInput 
          v-model="newDriver.last_name" 
          label="Отчество" 
          placeholder="Введите отчество"
          required
        />
        <TextInput 
          v-model="newDriver.login" 
          label="Логин" 
          placeholder="Введите логин"
          required
        />
        <TextInput 
          v-model="newDriver.password" 
          label="Пароль" 
          placeholder="Введите пароль"
          type="password"
          required
        />
        <TextInput 
          v-model="newDriver.phone" 
          label="Телефон" 
          placeholder="Введите телефон"
          required
        />
        <TextInput 
          v-model="newDriver.driver_license" 
          label="Водительское удостоверение" 
          placeholder="Введите номер удостоверения"
          required
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
        <TextInput 
          v-model="editingDriver.name" 
          label="Имя" 
          placeholder="Введите имя"
          required
        />
        <TextInput 
          v-model="editingDriver.surname" 
          label="Фамилия" 
          placeholder="Введите фамилию"
          required
        />
        <TextInput 
          v-model="editingDriver.last_name" 
          label="Отчество" 
          placeholder="Введите отчество"
          required
        />
        <TextInput 
          v-model="editingDriver.login" 
          label="Логин" 
          placeholder="Введите логин"
          required
        />
        <TextInput 
          v-model="editingDriver.password" 
          label="Пароль" 
          placeholder="Введите пароль (оставьте пустым, чтобы не менять)"
          type="password"
        />
        <TextInput 
          v-model="editingDriver.phone" 
          label="Телефон" 
          placeholder="Введите телефон"
          required
        />
        <TextInput 
          v-model="editingDriver.driver_license" 
          label="Водительское удостоверение" 
          placeholder="Введите номер удостоверения"
          required
        />
      </div>
      <template #footer>
        <Button variant="secondary" size="md" @click="closeEditModal">Закрыть</Button>
        <Button variant="primary" size="md" @click="updateDriver">Сохранить</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { DataTable, TextInput, palette, Modal, Button } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';

const auth = useAuthStore();
const drivers = ref([]);
const searchQuery = ref('');
const selectedDriverIds = ref([]);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);
const editingDriver = ref(null);

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
  role: 3, // role_id для водителей
});

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

const filteredDrivers = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return drivers.value.filter(driver =>
    driver.name.toLowerCase().includes(query) ||
    driver.surname.toLowerCase().includes(query) ||
    driver.last_name.toLowerCase().includes(query) ||
    driver.phone.includes(query) ||
    (driver.driver_license && driver.driver_license.includes(query))
  );
});

const driversToDelete = computed(() => {
  return filteredDrivers.value.filter(d => selectedDriverIds.value.includes(d.id));
});

const getSelectedIndexes = () => {
  return filteredDrivers.value
    .map((driver, index) => selectedDriverIds.value.includes(driver.id) ? index : -1)
    .filter(index => index !== -1);
};

const onRowsSelected = (selectedIndexes) => {
  selectedDriverIds.value = selectedIndexes.map(idx => filteredDrivers.value[idx].id);
};

const openAddModal = () => {
  resetNewDriver();
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  resetNewDriver();
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
  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на создание водителей.');
    return;
  }

  // Валидация полей
  if (!newDriver.value.name || !newDriver.value.surname || !newDriver.value.last_name || 
      !newDriver.value.login || !newDriver.value.password || !newDriver.value.phone || 
      !newDriver.value.driver_license) {
    console.warn('Все поля обязательны для заполнения.');
    alert('Пожалуйста, заполните все поля!');
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
    alert('Ошибка при добавлении водителя: ' + (error.response?.data?.detail || error.message));
  }
};

const onRowClick = (driver) => {
  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на редактирование водителей.');
    return;
  }
  openEditModal(driver);
};

const openEditModal = (driver) => {
  // Создаём копию водителя, чтобы не менять оригинальные данные при отмене
  editingDriver.value = { ...driver, password: '' };
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingDriver.value = null;
};

const updateDriver = async () => {
  if (!auth.permissions.can_create_users) {
    console.warn('Нет разрешения на редактирование водителей.');
    return;
  }

  if (!editingDriver.value) return;

  // Валидация полей
  if (!editingDriver.value.name || !editingDriver.value.surname || !editingDriver.value.last_name || 
      !editingDriver.value.login || !editingDriver.value.phone || 
      !editingDriver.value.driver_license) {
    console.warn('Все поля обязательны для заполнения.');
    alert('Пожалуйста, заполните все поля!');
    return;
  }

  try {
    // Если пароль не введён, не отправляем его на сервер
    const updateData = { ...editingDriver.value };
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
    alert('Ошибка при обновлении водителя: ' + (error.response?.data?.detail || error.message));
  }
};

const openDeleteModal = () => {
  if (selectedDriverIds.value.length === 0) {
    console.warn('Не выбраны водители для удаления.');
    return;
  }
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const confirmDelete = async () => {
  if (!auth.permissions.can_delete_users) {
    console.warn('Нет разрешения на удаление водителей.');
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
  }

  // Слушаем события от CrudPanel через App.vue
  window.addEventListener('crud:create', handleCrudCreate);
  window.addEventListener('crud:delete', handleCrudDelete);
});

onUnmounted(() => {
  // Очистить CRUD разрешения при выходе со страницы
  auth.clearCrudPermissions();
  
  // Удаляем слушатели событий
  window.removeEventListener('crud:create', handleCrudCreate);
  window.removeEventListener('crud:delete', handleCrudDelete);
});
</script>
