<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold" :style="{ color: palette.dark }">Аналитика расхода ГСМ</h1>
      </div>

      <!-- Filters Section -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 class="text-xl font-semibold mb-4" :style="{ color: palette.dark }">Фильтры</h2>
        <div class="flex flex-wrap gap-4">
          <div class="flex-shrink-0 min-w-[280px] mt-2 ">
            <DateRangeInput
              v-model="filters.dateRange"
              :label="'Период (опционально)'"
              :startLabel="'От'"
              :endLabel="'До'"
              :showClear="true"
            />
          </div>
          <div class="flex-shrink-0 min-w-[220px] mt-2" >
            <SelectInput
              v-model="filters.vehicle"
              label="Машина"
              :options="vehicleOptions"
              placeholder="Все машины"
            />
          </div>
          <div class="flex-shrink-0 min-w-[220px] mt-2">
            <SelectInput
              v-model="filters.driver"
              label="Водитель"
              :options="driverOptions"
              placeholder="Все водители"
            />
          </div>
          <div class="flex-shrink-0 min-w-[220px] mt-2">
            <SelectInput
              v-model="filters.vehicleType"
              label="Тип машины"
              :options="[
                { value: '', label: 'Все типы' },
                { value: 'fire_truck', label: 'Пожарные' },
                { value: 'passenger_car', label: 'Легковые' }
              ]"
              placeholder="Все типы"
            />
          </div>
        </div>
        <div class="flex flex-wrap gap-4 mt-4">
          <Button @click="loadAnalytics" variant="primary">Загрузить аналитику</Button>
          <Button @click="resetFilters" variant="secondary">Сбросить фильтры</Button>
          <Button @click="downloadReport" variant="primary" :style="{ backgroundColor: palette.success }">Скачать отчет (Excel)</Button>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div v-if="analytics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6 border-l-4" :style="{ borderColor: palette.primary }">
          <div class="text-sm font-medium" :style="{ color: palette.medium }">Расход топлива (факт)</div>
          <div class="text-3xl font-bold mt-2" :style="{ color: palette.dark }">{{ analytics.totalFuelUsed.toFixed(2) }} л</div>
          <div class="text-xs mt-2" :style="{ color: palette.light }">за выбранный период</div>
        </div>

        <div class="bg-white rounded-lg shadow p-6 border-l-4" :style="{ borderColor: palette.light }">
          <div class="text-sm font-medium" :style="{ color: palette.medium }">Пробег</div>
          <div class="text-3xl font-bold mt-2" :style="{ color: palette.dark }">{{ analytics.totalDistance.toFixed(0) }} км</div>
          <div class="text-xs mt-2" :style="{ color: palette.light }">всего пройдено</div>
        </div>
      </div>

      <!-- Norm vs Fact Cards -->
      <div v-if="analytics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6 border-l-4" :style="{ borderColor: palette.warning }">
          <div class="text-sm font-medium" :style="{ color: palette.medium }">Расход по норме</div>
          <div class="text-3xl font-bold mt-2" :style="{ color: palette.dark }">{{ analytics.totalFuelByNorm.toFixed(2) }} л</div>
          <div class="text-xs mt-2" :style="{ color: palette.light }">норма расхода</div>
        </div>

        <div class="bg-white rounded-lg shadow p-6 border-l-4" :style="{ borderColor: (analytics.totalFuelUsed - analytics.totalFuelByNorm) > 0 ? palette.danger : palette.success }">
          <div class="text-sm font-medium" :style="{ color: palette.medium }">Разница (факт - норма)</div>
          <div class="text-3xl font-bold mt-2" :style="{ color: (analytics.totalFuelUsed - analytics.totalFuelByNorm) > 0 ? palette.danger : palette.success }">
            {{ (analytics.totalFuelUsed - analytics.totalFuelByNorm).toFixed(2) }} л
          </div>
          <div class="text-xs mt-2" :style="{ color: (analytics.totalFuelUsed - analytics.totalFuelByNorm) > 0 ? palette.danger : palette.success }">
            <span v-if="(analytics.totalFuelUsed - analytics.totalFuelByNorm) > 0">перерасход</span>
            <span v-else-if="(analytics.totalFuelUsed - analytics.totalFuelByNorm) < 0">экономия</span>
          </div>
        </div>
      </div>

      <!-- Trip Count and Operating Hours Cards -->
      <div v-if="analytics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6 border-l-4" :style="{ borderColor: palette.primary }">
          <div class="text-sm font-medium" :style="{ color: palette.medium }">Суммарно поездок</div>
          <div class="text-3xl font-bold mt-2" :style="{ color: palette.dark }">{{ analytics.totalTripCount }}</div>
          <div class="text-xs mt-2" :style="{ color: palette.light }">всего выездов</div>
        </div>

        <div v-if="analytics.operatingHours > 0" class="bg-white rounded-lg shadow p-6 border-l-4" :style="{ borderColor: palette.success }">
          <div class="text-sm font-medium" :style="{ color: palette.medium }">Моточасы</div>
          <div class="text-3xl font-bold mt-2" :style="{ color: palette.dark }">{{ analytics.operatingHours.toFixed(2) }} ч</div>
          <div class="text-xs mt-2" :style="{ color: palette.light }">часов работы</div>
        </div>
      </div>

      <!-- Charts Grid - Row 0: Fact vs Norm + Operating Hours Over Time (2 columns) -->
      <div v-if="analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Fuel Fact vs Norm Over Time -->
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Фактический расход vs расход по норме</h3>
          <Line :data="chartFuelFactVsNorm" :options="chartOptions" />
        </div>

        <!-- Operating Hours Over Time (Area Chart) -->
        <div v-if="analytics.operatingHours > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Моточасы по дням</h3>
          <Line :data="chartOperatingHoursOverTime" :options="chartOptions" />
        </div>
      </div>

      <!-- Charts Grid - Row 1: By Driver and By Vehicle (2 columns) -->
      <div v-if="analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Left: Operating Hours by Driver (if vehicle selected) OR Fuel by Driver (if nothing selected) -->
        <div v-if="!filters.driver && analytics.summaryByDriver && analytics.summaryByDriver.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">
            {{ filters.vehicle ? 'Моточасы по водителям' : 'Расход по водителям' }}
          </h3>
          <Bar :data="filters.vehicle ? chartOperatingHoursByDriver : chartFuelByDriver" :options="chartOptions" />
        </div>

        <!-- Right: Fuel by Vehicle (if nothing selected) OR Operating Hours by Vehicle (if driver selected) -->
        <div v-if="!filters.vehicle && analytics.summaryByVehicle && analytics.summaryByVehicle.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">
            {{ filters.driver ? 'Моточасы по машинам' : 'Расход по машинам' }}
          </h3>
          <Bar :data="filters.driver ? chartOperatingHoursByVehicle : chartFuelByVehicle" :options="chartOptions" />
        </div>
      </div>

      <!-- Charts Grid - Row 2: Distributions by Distance (2 columns) -->
      <div v-if="analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Left: Distance Distribution by Driver or Operating Hours by Driver -->
        <div v-if="!filters.driver && analytics.summaryByDriver && analytics.summaryByDriver.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">
            {{ filters.vehicle ? 'Моточасы по водителям' : 'Распределение пробега по водителям' }}
          </h3>
          <Doughnut v-if="!filters.vehicle" :data="chartDriverDistanceDistribution" :options="chartOptions" />
          <Bar v-else :data="chartOperatingHoursByDriver" :options="chartOptions" />
        </div>

        <!-- Right: Distance Distribution by Vehicle or Operating Hours by Vehicle -->
        <div v-if="!filters.vehicle && analytics.summaryByVehicle && analytics.summaryByVehicle.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">
            {{ filters.driver ? 'Моточасы по машинам' : 'Распределение пробега по машинам' }}
          </h3>
          <Doughnut v-if="!filters.driver" :data="chartVehicleDistanceDistribution" :options="chartOptions" />
          <Bar v-else :data="chartOperatingHoursByVehicle" :options="chartOptions" />
        </div>
      </div>

      <!-- Summary Table -->
      <div v-if="analytics && analytics.summaryByVehicle.length > 0" class="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Сводка по машинам</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead :style="{ backgroundColor: palette.light + '20' }">
              <tr>
                <th class="px-4 py-2 text-left font-semibold" :style="{ color: palette.dark }">Машина</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Поездок</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Пробег, км</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Расход (факт)</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Норма</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Разница</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">л/100км</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in analytics.summaryByVehicle" :key="row.vehicleId" class="border-t">
                <td class="px-4 py-3" :style="{ color: palette.dark }">{{ row.vehicleName }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: palette.dark }">{{ row.tripCount }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: palette.dark }">{{ row.distance.toFixed(0) }}</td>
                <td class="px-4 py-3 text-right font-semibold" :style="{ color: palette.success }">{{ row.fuelUsed.toFixed(2) }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: palette.dark }">{{ row.fuelByNorm.toFixed(2) }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: (row.fuelUsed - row.fuelByNorm) > 0 ? palette.danger : (row.fuelUsed - row.fuelByNorm) < 0 ? palette.success : palette.light }">
                  <div>
                    <div class="font-semibold">{{ (row.fuelUsed - row.fuelByNorm).toFixed(2) }}</div>
                    <div class="text-xs">{{ (row.fuelUsed - row.fuelByNorm) > 0 ? 'перерасход' : (row.fuelUsed - row.fuelByNorm) < 0 ? 'экономия' : '' }}</div>
                  </div>
                </td>
                <td class="px-4 py-3 text-right font-semibold" :style="{ color: palette.primary }">{{ (row.fuelUsed / (row.distance || 1) * 100).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Driver Summary Table -->
      <div v-if="analytics && analytics.summaryByDriver.length > 0" class="bg-white rounded-lg shadow-lg p-6">
        <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Сводка по водителям</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead :style="{ backgroundColor: palette.light + '20' }">
              <tr>
                <th class="px-4 py-2 text-left font-semibold" :style="{ color: palette.dark }">Водитель</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Поездок</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Пробег, км</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Расход (факт)</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Норма</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">Разница</th>
                <th class="px-4 py-2 text-right font-semibold" :style="{ color: palette.dark }">л/100км</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in analytics.summaryByDriver" :key="row.driverId" class="border-t">
                <td class="px-4 py-3" :style="{ color: palette.dark }">{{ row.driverName }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: palette.dark }">{{ row.tripCount }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: palette.dark }">{{ row.distance.toFixed(0) }}</td>
                <td class="px-4 py-3 text-right font-semibold" :style="{ color: palette.success }">{{ row.fuelUsed.toFixed(2) }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: palette.dark }">{{ row.fuelByNorm.toFixed(2) }}</td>
                <td class="px-4 py-3 text-right" :style="{ color: (row.fuelUsed - row.fuelByNorm) > 0 ? palette.danger : (row.fuelUsed - row.fuelByNorm) < 0 ? palette.success : palette.light }">
                  <div>
                    <div class="font-semibold">{{ (row.fuelUsed - row.fuelByNorm).toFixed(2) }}</div>
                    <div class="text-xs">{{ (row.fuelUsed - row.fuelByNorm) > 0 ? 'перерасход' : (row.fuelUsed - row.fuelByNorm) < 0 ? 'экономия' : '' }}</div>
                  </div>
                </td>
                <td class="px-4 py-3 text-right font-semibold" :style="{ color: palette.primary }">{{ (row.fuelUsed / (row.distance || 1) * 100).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Report Info Modal -->
    <Modal
      :is-open="reportModalIsOpen"
      :title="reportModalTitle"
      @close="reportModalIsOpen = false"
    >
      <div class="space-y-4 min-w-96">
        <div class="rounded-lg p-4" :style="{ backgroundColor: `${palette.warning}15`, borderLeft: `4px solid ${palette.warning}` }">
          <p class="text-sm mt-2" :style="{ color: palette.dark }">{{ reportModalMessage }}</p>
        </div>
      </div>

      <template #footer>
        <Button variant="primary" size="md" @click="reportModalIsOpen = false">Закрыть</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { palette, SelectInput, Button, DateRangeInput, Modal } from '../components/ui/importUi';
import NavigationMenu from '../components/NavigationMenu.vue';
import { Line, Bar, Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import axios from 'axios';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement);

const auth = useAuthStore();
const router = useRouter();
const analytics = ref(null);
const waybillsData = ref([]);
const firetruck_data = ref([]);
const passenger_car_data = ref([]);
const drivers_data = ref([]);
const reportModalIsOpen = ref(false);
const reportModalMessage = ref('');
const reportModalTitle = ref('Внимание');

const filters = ref({
  dateRange: { start: '', end: '' },
  vehicle: '',
  driver: '',
  vehicleType: ''
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: true,
      labels: {
        color: palette.dark,
        font: { size: 12 }
      }
    }
  },
  scales: {
    y: {
      ticks: { color: palette.medium },
      grid: { color: palette.light + '40' }
    },
    x: {
      ticks: { color: palette.medium },
      grid: { color: palette.light + '40' }
    }
  }
};

const vehicleOptions = computed(() => {
  const options = [{ value: '', label: 'Все машины' }];
  
  if (filters.value.vehicleType === 'fire_truck' || !filters.value.vehicleType) {
    firetruck_data.value.forEach(truck => {
      options.push({
        value: `ft-${truck.id}`,
        label: `[Пожарн] ${truck.number} - ${truck.brand} ${truck.model}`
      });
    });
  }
  
  if (filters.value.vehicleType === 'passenger_car' || !filters.value.vehicleType) {
    passenger_car_data.value.forEach(car => {
      options.push({
        value: `pc-${car.id}`,
        label: `[Легков] ${car.number} - ${car.brand} ${car.model}`
      });
    });
  }
  
  return options;
});

const driverOptions = computed(() => {
  return [
    { value: '', label: 'Все водители' },
    ...drivers_data.value.map(driver => ({
      value: driver.id,
      label: `${driver.name} ${driver.last_name}`.trim()
    }))
  ];
});

const chartFuelFactVsNorm = computed(() => {
  if (!analytics.value) return {};
  
  return {
    labels: analytics.value.dailyFuel.map(d => d.date),
    datasets: [
      {
        label: 'Фактический расход (л)',
        data: analytics.value.dailyFuel.map(d => d.fuel),
        borderColor: palette.danger,
        backgroundColor: palette.danger + '20',
        tension: 0.3,
        fill: true
      },
      {
        label: 'Норма (л)',
        data: analytics.value.dailyFuel.map(d => d.norm),
        borderColor: palette.success,
        backgroundColor: palette.success + '20',
        tension: 0.3,
        fill: true
      }
    ]
  };
});

const chartFuelByVehicle = computed(() => {
  if (!analytics.value || !analytics.value.summaryByVehicle || analytics.value.summaryByVehicle.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByVehicle.map(v => v.vehicleName),
    datasets: [{
      label: 'Расход топлива (л)',
      data: analytics.value.summaryByVehicle.map(v => v.fuelUsed),
      backgroundColor: analytics.value.summaryByVehicle.map((_, i) => colors[i % colors.length])
    }]
  };
});

const chartFuelByDriver = computed(() => {
  if (!analytics.value || !analytics.value.summaryByDriver || analytics.value.summaryByDriver.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByDriver.map(d => d.driverName),
    datasets: [{
      label: 'Расход топлива (л)',
      data: analytics.value.summaryByDriver.map(d => d.fuelUsed),
      backgroundColor: analytics.value.summaryByDriver.map((_, i) => colors[i % colors.length])
    }]
  };
});

const chartVehicleDistribution = computed(() => {
  if (!analytics.value || !analytics.value.summaryByVehicle || analytics.value.summaryByVehicle.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByVehicle.map(v => v.vehicleName),
    datasets: [{
      data: analytics.value.summaryByVehicle.map(v => v.fuelUsed),
      backgroundColor: analytics.value.summaryByVehicle.map((_, i) => colors[i % colors.length]),
      borderColor: '#fff',
      borderWidth: 2
    }]
  };
});

// Распределение пробега по машинам
const chartVehicleDistanceDistribution = computed(() => {
  if (!analytics.value || !analytics.value.summaryByVehicle || analytics.value.summaryByVehicle.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByVehicle.map(v => v.vehicleName),
    datasets: [{
      data: analytics.value.summaryByVehicle.map(v => v.distance || 0),
      backgroundColor: analytics.value.summaryByVehicle.map((_, i) => colors[i % colors.length]),
      borderColor: '#fff',
      borderWidth: 2
    }]
  };
});

const chartDriverDistribution = computed(() => {
  if (!analytics.value || !analytics.value.summaryByDriver || analytics.value.summaryByDriver.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByDriver.map(d => d.driverName),
    datasets: [{
      data: analytics.value.summaryByDriver.map(d => d.fuelUsed),
      backgroundColor: analytics.value.summaryByDriver.map((_, i) => colors[i % colors.length]),
      borderColor: '#fff',
      borderWidth: 2
    }]
  };
});

// Распределение пробега по водителям
const chartDriverDistanceDistribution = computed(() => {
  if (!analytics.value || !analytics.value.summaryByDriver || analytics.value.summaryByDriver.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByDriver.map(d => d.driverName),
    datasets: [{
      data: analytics.value.summaryByDriver.map(d => d.distance || 0),
      backgroundColor: analytics.value.summaryByDriver.map((_, i) => colors[i % colors.length]),
      borderColor: '#fff',
      borderWidth: 2
    }]
  };
});

const chartOperatingHoursByDriver = computed(() => {
  if (!analytics.value || !analytics.value.summaryByDriver || analytics.value.summaryByDriver.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByDriver.map(d => d.driverName),
    datasets: [{
      label: 'Моточасы (ч)',
      data: analytics.value.summaryByDriver.map(d => d.operatingHours || 0),
      backgroundColor: analytics.value.summaryByDriver.map((_, i) => colors[i % colors.length])
    }]
  };
});

const chartOperatingHoursByVehicle = computed(() => {
  if (!analytics.value || !analytics.value.summaryByVehicle || analytics.value.summaryByVehicle.length === 0) return {};
  
  const colors = [
    palette.primary,
    palette.success,
    palette.warning,
    palette.danger,
    '#3b82f6', // blue
    '#10b981', // emerald
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#14b8a6'  // teal
  ];
  
  return {
    labels: analytics.value.summaryByVehicle.map(v => v.vehicleName),
    datasets: [{
      label: 'Моточасы (ч)',
      data: analytics.value.summaryByVehicle.map(v => v.operatingHours || 0),
      backgroundColor: analytics.value.summaryByVehicle.map((_, i) => colors[i % colors.length])
    }]
  };
});

// Area Chart для моточасов по дням (Line с fill)
const chartOperatingHoursOverTime = computed(() => {
  if (!analytics.value || !analytics.value.dailyFuel || analytics.value.dailyFuel.length === 0) return {};
  
  return {
    labels: analytics.value.dailyFuel.map(d => d.date),
    datasets: [{
      label: 'Моточасы (ч)',
      data: analytics.value.dailyFuel.map(d => d.operatingHours || 0),
      borderColor: palette.success,
      backgroundColor: palette.success + '40',
      tension: 0.3,
      fill: true,
      pointRadius: 4,
      pointBackgroundColor: palette.success,
      pointBorderColor: '#fff',
      pointBorderWidth: 2
    }]
  };
});

// Load initial data
onMounted(async () => {
  // Дополнительная проверка - водитель не должен быть здесь
  if (auth.isDriver()) {
    console.error('[FuelReport] Driver somehow accessed FuelReport, redirecting...');
    auth.logout();
    router.replace('/auth');
    return;
  }

  // Проверить, есть ли доступ к отчетам
  if (!auth.canAccessReports()) {
    console.warn('[FuelReport] User does not have access to any reports, redirecting...');
    
    // Если нет доступа к отчетам, проверить есть ли доступ к Users
    if (auth.permissions.view_users) {
      router.replace('/users');
    } else {
      // Если и на Users нет прав, то что-то не так с ролью
      console.error('[FuelReport] User has no access to reports or users - role configuration issue');
      router.replace('/');
    }
    return;
  }

  try {
    // Load vehicles
    const firetrucksRes = await axios.get('/fire-trucks/');
    firetruck_data.value = Array.isArray(firetrucksRes.data) ? firetrucksRes.data : firetrucksRes.data.results || [];

    const carsRes = await axios.get('/passenger-cars/');
    passenger_car_data.value = Array.isArray(carsRes.data) ? carsRes.data : carsRes.data.results || [];

    // Load drivers (use /users/drivers/ endpoint which mechanics have permission for)
    const driversRes = await axios.get('/users/drivers/');
    drivers_data.value = Array.isArray(driversRes.data) ? driversRes.data : driversRes.data.results || [];
    console.log('[FuelReport] Loaded drivers:', drivers_data.value.length > 0 ? drivers_data.value.map(d => ({ id: d.id, name: `${d.name} ${d.last_name}` })) : 'EMPTY');
    
    // Auto-load analytics on page load
    await loadAnalytics();
  } catch (error) {
    console.error('Error loading data:', error);
  }
});

// Debounced analytics loader
let loadAnalyticsTimeout;
const debouncedLoadAnalytics = () => {
  clearTimeout(loadAnalyticsTimeout);
  loadAnalyticsTimeout = setTimeout(() => {
    loadAnalytics();
  }, 300);
};

// When vehicle type changes, clear the selected vehicle and reload
watch(
  () => filters.value.vehicleType,
  (newType) => {
    filters.value.vehicle = '';
    debouncedLoadAnalytics();
  }
);

// Auto-load when vehicle changes
watch(
  () => filters.value.vehicle,
  () => {
    debouncedLoadAnalytics();
  }
);

// Auto-load when driver changes
watch(
  () => filters.value.driver,
  () => {
    debouncedLoadAnalytics();
  }
);

// Auto-load when date range changes
watch(
  () => filters.value.dateRange,
  () => {
    debouncedLoadAnalytics();
  },
  { deep: true }
);

const resetFilters = () => {
  filters.value = {
    dateRange: { start: '', end: '' },
    vehicle: '',
    driver: '',
    vehicleType: ''
  };
  analytics.value = null;
};

const loadAnalytics = async () => {
  try {
    // Prepare parameters for statistics endpoint  
    // Даты опциональны - если не указаны, загружается статистика за всё время
    const params = new URLSearchParams();
    if (filters.value.dateRange.start) params.append('from', filters.value.dateRange.start);
    if (filters.value.dateRange.end) params.append('to', filters.value.dateRange.end);
    
    // Determine vehicle type for statistics
    let vehicleType = 'all';
    if (filters.value.vehicleType === 'fire_truck') vehicleType = 'fire-truck';
    else if (filters.value.vehicleType === 'passenger_car') vehicleType = 'passenger-car';
    
    params.append('vehicle_type', vehicleType);
    
    // Add vehicle_id if selected (format: "ft-123" or "pc-456")
    if (filters.value.vehicle) {
      const [type, vehicleId] = filters.value.vehicle.split('-');
      params.append('vehicle_type_prefix', type);
      params.append('vehicle_id', vehicleId);
    }
    
    // Add driver_id if selected
    if (filters.value.driver) {
      params.append('driver_id', filters.value.driver);
    }

    // Fetch statistics from backend
    const statsRes = await axios.get(`/statistics/summary/?${params.toString()}`);
    const stats = statsRes.data;

    console.log('[FuelReport] Loaded statistics from backend:', stats);
    console.log('[FuelReport] Number of drivers:', stats.drivers?.length || 0);
    console.log('[FuelReport] Drivers list:', stats.drivers);
    console.log('[FuelReport] Number of daily fuel entries:', stats.daily_fuel?.length || 0);

    // Transform backend statistics format to frontend analytics format
    let vehicleList = [];
    let driverList = {};

    // Process passenger cars
    if (Array.isArray(stats.passenger_cars)) {
      stats.passenger_cars.forEach(car => {
        vehicleList.push({
          vehicleId: car.id,
          vehicleName: `${car.number} - ${car.brand} ${car.model}`,
          tripCount: car.trip_count,
          distance: car.distance,
          fuelUsed: car.fuel_used,
          fuelByNorm: car.fuel_by_norm,
          operatingHours: car.operating_hours || 0
        });
      });
    }

    // Process fire trucks
    if (Array.isArray(stats.fire_trucks)) {
      stats.fire_trucks.forEach(truck => {
        vehicleList.push({
          vehicleId: `ft_${truck.id}`,
          vehicleName: `${truck.number} - ${truck.brand} ${truck.model}`,
          tripCount: truck.trip_count,
          distance: truck.distance,
          fuelUsed: truck.fuel_used,
          fuelByNorm: truck.fuel_by_norm,
          operatingHours: truck.operating_hours || 0
        });
      });
    }

    // Process drivers
    if (Array.isArray(stats.drivers)) {
      console.log('[FuelReport] Processing drivers from stats:', stats.drivers);
      console.log('[FuelReport] Driver filter value:', filters.value.driver);
      stats.drivers.forEach(driver => {
        console.log(`[FuelReport] Adding driver ${driver.id} (${driver.name})`);
        driverList[driver.id] = {
          driverId: driver.id,
          driverName: driver.name,  // ← Используем name как есть, это уже полное имя
          tripCount: driver.trip_count,
          distance: driver.distance,
          fuelUsed: driver.fuel_used,
          fuelByNorm: driver.fuel_by_norm,
          operatingHours: driver.operating_hours || 0
        };
      });
    }

    // Build analytics from backend statistics
    analytics.value = {
      totalFuelUsed: stats.total.fuel_used,
      totalFuelByNorm: stats.total.fuel_by_norm,
      totalDistance: stats.total.distance,
      tripCount: stats.total.trip_count,
      totalTripCount: stats.total.trip_count,
      operatingHours: stats.total.operating_hours || 0,
      dailyFuel: Array.isArray(stats.daily_fuel) ? stats.daily_fuel.map(item => ({
        date: item.date,
        fuel: item.fuel_used,
        norm: item.fuel_by_norm,
        operatingHours: item.operating_hours || 0
      })) : [],
      summaryByVehicle: vehicleList.sort((a, b) => b.fuelUsed - a.fuelUsed),
      summaryByDriver: Object.values(driverList).sort((a, b) => b.fuelUsed - a.fuelUsed)
    };

    console.log('[FuelReport] Analytics built from statistics:', analytics.value);

  } catch (error) {
    console.error('Error loading analytics:', error);
  }
};

const downloadReport = async () => {
  try {
    // Check if driver is selected
    if (!filters.value.driver) {
      reportModalTitle.value = 'Отчеты не поддерживаются для типа машины';
      reportModalMessage.value = 'Отчеты доступны только для конкретного водителя. Пожалуйста, выберите водителя из списка.';
      reportModalIsOpen.value = true;
      return;
    }

    // Check if dates are selected (required by server)
    if (!filters.value.dateRange.start || !filters.value.dateRange.end) {
      reportModalTitle.value = 'Ошибка: даты не указаны';
      reportModalMessage.value = 'Для скачивания отчета необходимо указать период (от и до).';
      reportModalIsOpen.value = true;
      return;
    }

    // Build query parameters
    const params = new URLSearchParams();
    params.append('driver', filters.value.driver);
    params.append('from', filters.value.dateRange.start);
    params.append('to', filters.value.dateRange.end);

    // Download the report
    const response = await axios.get(`/users/drivers-report-excel/?${params.toString()}`, {
      responseType: 'blob'
    });

    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    // Get driver name for filename
    const driver = drivers_data.value.find(d => d.id == filters.value.driver);
    const driverName = driver ? `${driver.surname}_${driver.name}` : `driver_${filters.value.driver}`;
    const dateStr = new Date().toISOString().split('T')[0];
    
    link.setAttribute('download', `report_${driverName}_${dateStr}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    console.log('[FuelReport] Report downloaded successfully');
  } catch (error) {
    console.error('[FuelReport] Error downloading report:', error);
    reportModalTitle.value = 'Ошибка при скачивании';
    reportModalMessage.value = error.response?.data?.detail || 'Не удалось скачать отчет. Пожалуйста, попробуйте еще раз.';
    reportModalIsOpen.value = true;
  }
};

</script>
