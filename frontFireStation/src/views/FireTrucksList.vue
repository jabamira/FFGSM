<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Список пожарных автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <template v-if="permissions.can_create_fire_trucks">
          <Button label="Добавить автомобиль" variant="primary" @click="openAddModal" class="mb-4" />
        </template>
        <TextInput v-model="searchQuery" label="Поиск" placeholder="Введите данные для поиска" class="mb-4" />
        <DataTable :data="filteredFireTrucks" :columns="columns" @row-click="permissions.can_update_fire_trucks ? openEditModal : null">
          <template #actions="{ row }">
            <Button v-if="permissions.can_delete_fire_trucks" label="Удалить" variant="danger" @click="deleteFireTruck(row.id)" />
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Add Fire Truck Modal -->
    <Modal :is-open="isAddModalOpen" title="Добавить автомобиль" @close="closeAddModal">
      <form @submit.prevent="addFireTruck">
        <TextInput v-model="newFireTruck.number" label="Гос. номер" required />
        <TextInput v-model="newFireTruck.brand" label="Марка" required />
        <TextInput v-model="newFireTruck.model" label="Модель" required />
        <Button label="Сохранить" variant="primary" type="submit" />
      </form>
    </Modal>

    <!-- Edit Fire Truck Modal -->
    <Modal :is-open="isEditModalOpen" title="Редактировать данные" @close="closeEditModal">
      <form @submit.prevent="saveFireTruck">
        <TextInput v-model="editableFireTruck.number" label="Гос. номер" required />
        <TextInput v-model="editableFireTruck.brand" label="Марка" required />
        <TextInput v-model="editableFireTruck.model" label="Модель" required />
        <Button label="Сохранить" variant="primary" type="submit" />
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { DataTable, TextInput, Modal, Button, palette } from '../components/ui/importUi';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import NavigationMenu from '../components/NavigationMenu.vue';

const auth = useAuthStore();
const fireTrucks = ref([]);
const searchQuery = ref('');
const isAddModalOpen = ref(false);
const isEditModalOpen = ref(false);
const newFireTruck = ref({ number: '', brand: '', model: '' });
const editableFireTruck = ref({});
const permissions = computed(() => auth.permissions);

const columns = [
  { key: 'number', label: 'Гос. номер' },
  { key: 'brand', label: 'Марка' },
  { key: 'model', label: 'Модель' },
  { key: 'actions', label: 'Действия', slot: true }
];

const fetchFireTrucks = async () => {
  if (!permissions.value.view_fire_trucks) {
    console.warn("Нет разрешения на просмотр транспортных средств.");
    return;
  }

  try {
    const response = await axios.get('/fire-trucks', {
      headers: { Authorization: `Bearer ${auth.token}` },
    });
    fireTrucks.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке пожарных автомобилей:", error);
  }
};

const filteredFireTrucks = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return fireTrucks.value.filter(truck =>
    truck.number.toLowerCase().includes(query) ||
    truck.brand.toLowerCase().includes(query) ||
    truck.model.toLowerCase().includes(query)
  );
});

const openAddModal = () => {
  isAddModalOpen.value = true;
};

const closeAddModal = () => {
  isAddModalOpen.value = false;
};

const addFireTruck = async () => {
  try {
    await axios.post('/fire-trucks/', newFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchFireTrucks();
    closeAddModal();
  } catch (error) {
    console.error('Ошибка при добавлении автомобиля:', error);
  }
};

const openEditModal = (truck) => {
  editableFireTruck.value = { ...truck };
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
};

const saveFireTruck = async () => {
  try {
    await axios.put(`/fire-trucks/${editableFireTruck.value.id}/`, editableFireTruck.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchFireTrucks();
    closeEditModal();
  } catch (error) {
    console.error('Ошибка при сохранении данных:', error);
  }
};

const deleteFireTruck = async (id) => {
  try {
    await axios.delete(`/fire-trucks/${id}/`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    fetchFireTrucks();
  } catch (error) {
    console.error('Ошибка при удалении автомобиля:', error);
  }
};

onMounted(() => {
  console.debug("[DEBUG] Permissions loaded from store:", auth.permissions);
  if (auth.permissions.view_fire_trucks) {
    fetchFireTrucks();
  } else {
    console.warn("[DEBUG] User does not have permission to view fire trucks.");
  }
});
</script>
