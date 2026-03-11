<template>
  <nav class="bg-white shadow-md border-b" :style="{ borderColor: palette.light }">
    <div class="max-w-7xl mx-auto px-4 py-2 flex items-center gap-4">
      <h1 class="text-lg font-bold" :style="{ color: palette.dark }">Управление ГСМ</h1>
      <div class="flex items-center gap-2">
        <router-link 
          v-if="auth.user && auth.permissions && auth.permissions.view_drivers"
          to="/drivers" 
          :class="['px-3 py-1.5 rounded transition', isActive('/drivers') ? 'font-semibold' : 'hover:bg-gray-100']"
          :style="isActive('/drivers') ? { color: palette.primary, backgroundColor: palette.primary + '10' } : { color: palette.dark }"
        >
          Водители
        </router-link>
        <router-link 
          v-if="auth.user && auth.permissions && auth.permissions.view_users"
          to="/users" 
          :class="['px-3 py-1.5 rounded transition', isActive('/users') ? 'font-semibold' : 'hover:bg-gray-100']"
          :style="isActive('/users') ? { color: palette.primary, backgroundColor: palette.primary + '10' } : { color: palette.dark }"
        >
          Пользователи
        </router-link>
          <router-link 
            v-if="auth.user && auth.permissions && auth.permissions.can_view_roles"
            to="/roles" 
            :class="['px-3 py-1.5 rounded transition', isActive('/roles') ? 'font-semibold' : 'hover:bg-gray-100']"
            :style="isActive('/roles') ? { color: palette.primary, backgroundColor: palette.primary + '10' } : { color: palette.dark }"
          >
            Роли
          </router-link>
        <div v-if="auth.user && auth.permissions && canViewFireTrucks()" class="relative group">
          <button
            :class="['px-3 py-1.5 rounded transition flex items-center gap-2', isFireTruckActive() ? 'font-semibold' : 'hover:bg-gray-100']"
            :style="isFireTruckActive() ? { color: palette.primary, backgroundColor: palette.primary + '10' } : { color: palette.dark }"
          >
            Пожарные автомобили
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
            </svg>
          </button>
          <div class="hidden group-hover:block absolute left-0 top-full mt-0 w-48 bg-white rounded shadow-lg z-50 border" :style="{ borderColor: palette.light }">
            <router-link 
              v-if="auth.permissions && auth.permissions.view_fire_trucks"
              to="/fire-trucks-list" 
              class="block px-4 py-2 hover:bg-gray-50 first:rounded-t-md"
              :style="{ color: palette.dark }"
            >
              Список пожарных автомобилей
            </router-link>
            <router-link 
              v-if="auth.permissions && auth.permissions.view_fire_truck_waybills"
              to="/fire-trucks-waybills" 
              class="block px-4 py-2 hover:bg-gray-50"
              :style="{ color: palette.dark }"
            >
              Путевые листы
            </router-link>
            <router-link 
              v-if="auth.permissions && auth.permissions.view_fire_truck_norms"
              to="/fire-trucks-norms" 
              class="block px-4 py-2 hover:bg-gray-50 last:rounded-b-md"
              :style="{ color: palette.dark }"
            >
              Нормы для машин
            </router-link>
          </div>
        </div>
        <div v-if="auth.user && auth.permissions && canViewPassengerCars()" class="relative group">
          <button
            :class="['px-3 py-1.5 rounded transition flex items-center gap-2', isLightVehicleActive() ? 'font-semibold' : 'hover:bg-gray-100']"
            :style="isLightVehicleActive() ? { color: palette.primary, backgroundColor: palette.primary + '10' } : { color: palette.dark }"
          >
            Легковые автомобили
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
            </svg>
          </button>
          <div class="hidden group-hover:block absolute left-0 top-full mt-0 w-48 bg-white rounded shadow-lg z-50 border" :style="{ borderColor: palette.light }">
            <router-link 
              v-if="auth.permissions && auth.permissions.view_passenger_cars"
              to="/light-vehicles-list" 
              class="block px-4 py-2 hover:bg-gray-50 first:rounded-t-md"
              :style="{ color: palette.dark }"
            >
              Список легковых автомобилей
            </router-link>
            <router-link 
              v-if="auth.permissions && auth.permissions.view_passenger_cars_waybills"
              to="/light-vehicles-waybills" 
              class="block px-4 py-2 hover:bg-gray-50"
              :style="{ color: palette.dark }"
            >
              Путевые листы
            </router-link>
            <router-link 
              v-if="auth.permissions && auth.permissions.view_passenger_cars_norms"
              to="/light-vehicles-norms"
              class="block px-4 py-2 hover:bg-gray-50 last:rounded-b-md"
              :style="{ color: palette.dark }"
            >
              Нормы для машин
            </router-link>
          </div>
        </div>
        <router-link 
          v-if="auth.user && auth.permissions && auth.permissions.view_fire_truck_reports"
          to="/fuel-report" 
          :class="['px-3 py-1.5 rounded transition', isActive('/fuel-report') ? 'font-semibold' : 'hover:bg-gray-100']"
          :style="isActive('/fuel-report') ? { color: palette.primary, backgroundColor: palette.primary + '10' } : { color: palette.dark }"
        >
          Отчёт по ГСМ
        </router-link>
      </div>
      <div class="ml-auto">
        <Button 
          @click="logout" 
          label="Выход"
          variant="secondary"
        />
      </div>
    </div>

   
  </nav>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { palette, Button } from './ui/importUi';
import { onMounted } from 'vue';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

console.debug("[NavigationMenu] Auth store:", auth); // Debug the auth object

const isActive = (path) => {
  return route.path === path;
};

const isFireTruckActive = () => {
  return ['/fire-trucks-list', '/fire-trucks-waybills', '/fire-trucks-norms'].includes(route.path);
};

const isLightVehicleActive = () => {
  return ['/light-vehicles-list', '/light-vehicles-waybills', '/light-vehicles-norms'].includes(route.path);
};

/**
 * Проверить, есть ли хотя бы одно разрешение для просмотра пожарных автомобилей
 */
const canViewFireTrucks = () => {
  if (!auth.permissions) return false;
  return !!(
    auth.permissions.view_fire_trucks ||
    auth.permissions.view_fire_truck_waybills ||
    auth.permissions.view_fire_truck_norms
  );
};

/**
 * Проверить, есть ли хотя бы одно разрешение для просмотра легковых автомобилей
 */
const canViewPassengerCars = () => {
  if (!auth.permissions) return false;
  return !!(
    auth.permissions.view_passenger_cars ||
    auth.permissions.view_passenger_cars_waybills ||
    auth.permissions.view_passenger_cars_norms
  );
};

const logout = () => {
  auth.setAccess(null);
  auth.setUser(null);
  router.push('/auth');
};

// Fetch permissions on component mount
onMounted(async () => {
  if (!auth.permissions || Object.keys(auth.permissions).length === 0) {
    try {
      await auth.fetchPermissions();
    } catch (error) {
      console.error("[NavigationMenu] Error fetching permissions:", error);
    }
  }
});
</script>

<style scoped>
nav {
  position: sticky;
  top: 0;
  z-index: 40;
}
</style>
