<template>
  <Modal
    :is-open="isOpen"
    title="Доступ запрещен"
    @close="closeModal"
  >
    <div class="space-y-4 min-w-96">
      <div class="flex flex-col items-center">
        <div class="flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
          <svg class="h-8 w-8 text-red-600" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M5.25 10.0546V8C5.25 4.27208 8.27208 1.25 12 1.25C15.7279 1.25 18.75 4.27208 18.75 8V10.0546C19.8648 10.1379 20.5907 10.348 21.1213 10.8787C22 11.7574 22 13.1716 22 16C22 18.8284 22 20.2426 21.1213 21.1213C20.2426 22 18.8284 22 16 22H8C5.17157 22 3.75736 22 2.87868 21.1213C2 20.2426 2 18.8284 2 16C2 13.1716 2 11.7574 2.87868 10.8787C3.40931 10.348 4.13525 10.1379 5.25 10.0546ZM6.75 8C6.75 5.10051 9.10051 2.75 12 2.75C14.8995 2.75 17.25 5.10051 17.25 8V10.0036C16.867 10 16.4515 10 16 10H8C7.54849 10 7.13301 10 6.75 10.0036V8Z" fill="currentColor"></path>
          </svg>
        </div>
        <p :style="{ color: palette.dark }" class="font-semibold text-center">У вас нет необходимого разрешения</p>
        <p class="text-gray-600 text-sm mt-3 text-center">
          Для выполнения этого действия требуется разрешение:
        </p>
        <div class="mt-4 bg-gray-50 border border-gray-200 rounded p-4 w-full">
          <p class="text-sm font-medium text-gray-900 text-center">
            {{ permissionLabel }}
          </p>
          <p class="text-xs text-gray-500 mt-3 text-center">
            Код разрешения: <code class="bg-gray-200 px-2 py-1 rounded">{{ permissionCode }}</code>
          </p>
        </div>
      </div>
    </div>
    <template #footer>
      <Button variant="primary" size="md" @click="closeModal">Понятно</Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Modal, Button, palette } from './ui/importUi';

const isOpen = ref(false);
const permissionCode = ref('');

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

const permissionLabel = computed(() => {
  return permissionsMap[permissionCode.value] || permissionCode.value;
});

const openModal = (code) => {
  permissionCode.value = code;
  isOpen.value = true;
};

const closeModal = () => {
  isOpen.value = false;
  permissionCode.value = '';
};

defineExpose({
  openModal,
  closeModal
});
</script>
