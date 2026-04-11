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

      <!-- Charts Grid - Row 0: Daily Fuel -->
      <div v-if="analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Fuel Over Time -->
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Расход топлива по дням</h3>
          <Line :data="chartFuelOverTime" :options="chartOptions" />
        </div>

        <!-- Fuel Fact vs Norm Over Time -->
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Факт vs Норма по дням</h3>
          <Line :data="chartFuelFactVsNorm" :options="chartOptions" />
        </div>
      </div>

      <!-- Charts Grid - Row 1: By Driver and By Vehicle -->
      <div v-if="analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Fuel by Driver -->
        <div v-if="!filters.driver && analytics.summaryByDriver && analytics.summaryByDriver.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Расход по водителям</h3>
          <Bar :data="chartFuelByDriver" :options="chartOptions" />
        </div>

        <!-- Fuel by Vehicle -->
        <div v-if="!filters.vehicle && analytics.summaryByVehicle && analytics.summaryByVehicle.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Расход по машинам</h3>
          <Bar :data="chartFuelByVehicle" :options="chartOptions" />
        </div>
      </div>

      <!-- Charts Grid - Row 2: Distributions -->
      <div v-if="analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Driver Distribution -->
        <div v-if="!filters.driver && analytics.summaryByDriver && analytics.summaryByDriver.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">Распределение по водителям</h3>
          <Doughnut :data="chartDriverDistribution" :options="chartOptions" />
        </div>

        <!-- Vehicle Distribution -->
        <div v-if="!filters.vehicle && analytics.summaryByVehicle && analytics.summaryByVehicle.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.dark }">
Распределение по машинам</h3>
          <Doughnut :data="chartVehicleDistribution" :options="chartOptions" />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { palette, SelectInput, Button, DateRangeInput } from '../components/ui/importUi';
import NavigationMenu from '../components/NavigationMenu.vue';
import { Line, Bar, Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import axios from 'axios';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement);

const auth = useAuthStore();
const analytics = ref(null);
const waybillsData = ref([]);
const firetruck_data = ref([]);
const passenger_car_data = ref([]);
const drivers_data = ref([]);

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

const chartFuelOverTime = computed(() => {
  if (!analytics.value) return {};
  
  return {
    labels: analytics.value.dailyFuel.map(d => d.date),
    datasets: [{
      label: 'Расход топлива (л)',
      data: analytics.value.dailyFuel.map(d => d.fuel),
      borderColor: palette.primary,
      backgroundColor: palette.primary + '20',
      tension: 0.3,
      fill: true
    }]
  };
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

// Load initial data
onMounted(async () => {
  try {
    // Load vehicles
    const firetrucksRes = await axios.get('/fire-trucks/');
    firetruck_data.value = Array.isArray(firetrucksRes.data) ? firetrucksRes.data : firetrucksRes.data.results || [];

    const carsRes = await axios.get('/passenger-cars/');
    passenger_car_data.value = Array.isArray(carsRes.data) ? carsRes.data : carsRes.data.results || [];

    // Load drivers
    const driversRes = await axios.get('/users/');
    drivers_data.value = Array.isArray(driversRes.data) ? driversRes.data : driversRes.data.results || [];
    console.log('[FuelReport] Loaded drivers:', drivers_data.value.length > 0 ? drivers_data.value.map(d => ({ id: d.id, name: `${d.name} ${d.last_name}` })) : 'EMPTY');
  } catch (error) {
    console.error('Error loading data:', error);
  }
});

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
        // Apply vehicle filter if specified
        if (filters.value.vehicle) {
          const [type, vehicleId] = filters.value.vehicle.split('-');
          if (type !== 'pc' || parseInt(vehicleId) !== car.id) return;
        }

        vehicleList.push({
          vehicleId: car.id,
          vehicleName: `${car.number} - ${car.brand} ${car.model}`,
          tripCount: car.trip_count,
          distance: car.distance,
          fuelUsed: car.fuel_used,
          fuelByNorm: car.fuel_by_norm
        });
      });
    }

    // Process fire trucks
    if (Array.isArray(stats.fire_trucks)) {
      stats.fire_trucks.forEach(truck => {
        // Apply vehicle filter if specified
        if (filters.value.vehicle) {
          const [type, vehicleId] = filters.value.vehicle.split('-');
          if (type !== 'ft' || parseInt(vehicleId) !== truck.id) return;
        }

        vehicleList.push({
          vehicleId: `ft_${truck.id}`,
          vehicleName: `${truck.number} - ${truck.brand} ${truck.model}`,
          tripCount: truck.trip_count,
          distance: truck.distance,
          fuelUsed: truck.fuel_used,
          fuelByNorm: truck.fuel_by_norm
        });
      });
    }

    // Process drivers
    if (Array.isArray(stats.drivers)) {
      console.log('[FuelReport] Processing drivers from stats:', stats.drivers);
      console.log('[FuelReport] Driver filter value:', filters.value.driver);
      stats.drivers.forEach(driver => {
        // Apply driver filter if specified
        if (filters.value.driver && parseInt(filters.value.driver) !== driver.id) {
          console.log(`[FuelReport] Filtering out driver ${driver.id} (${driver.name}) - filter value: ${filters.value.driver}`);
          return;
        }

        console.log(`[FuelReport] Adding driver ${driver.id} (${driver.name})`);
        driverList[driver.id] = {
          driverId: driver.id,
          driverName: `${driver.name} ${driver.last_name}`.trim(),
          tripCount: driver.trip_count,
          distance: driver.distance,
          fuelUsed: driver.fuel_used,
          fuelByNorm: driver.fuel_by_norm
        };
      });
    }

    // Build analytics from backend statistics
    analytics.value = {
      totalFuelUsed: stats.total.fuel_used,
      totalFuelByNorm: stats.total.fuel_by_norm,
      totalDistance: stats.total.distance,
      tripCount: stats.total.trip_count,
      dailyFuel: Array.isArray(stats.daily_fuel) ? stats.daily_fuel.map(item => ({
        date: item.date,
        fuel: item.fuel_used,
        norm: item.fuel_by_norm
      })) : [],
      summaryByVehicle: vehicleList.sort((a, b) => b.fuelUsed - a.fuelUsed),
      summaryByDriver: Object.values(driverList).sort((a, b) => b.fuelUsed - a.fuelUsed)
    };

    console.log('[FuelReport] Analytics built from statistics:', analytics.value);

  } catch (error) {
    console.error('Error loading analytics:', error);
  }
};

const buildAnalytics = () => {
  if (waybillsData.value.length === 0) {
    analytics.value = {
      totalFuelUsed: 0,
      totalFuelByNorm: 0,
      totalDistance: 0,
      tripCount: 0,
      dailyFuel: [],
      summaryByVehicle: [],
      summaryByDriver: []
    };
    return;
  }

  const dailyMap = {};
  const vehicleMap = {};
  const driverMap = {};
  let totalFuelUsed = 0;
  let totalFuelByNorm = 0;
  let totalDistance = 0;
  let totalTripCount = 0;

  waybillsData.value.forEach(waybill => {
    // Aggregate by day
    const dateKey = waybill.date;
    if (!dailyMap[dateKey]) dailyMap[dateKey] = { fuelUsed: 0, fuelByNorm: 0 };
    dailyMap[dateKey].fuelUsed += parseFloat(waybill.total_spent || 0);
    dailyMap[dateKey].fuelByNorm += parseFloat(waybill.required_by_norm || 0);

    // Aggregate by vehicle
    const vehicleKey = waybill.car;
    const vehicle = firetruck_data.value.find(v => v.id === vehicleKey) || 
                    passenger_car_data.value.find(v => v.id === vehicleKey);
    
    if (!vehicleMap[vehicleKey]) {
      vehicleMap[vehicleKey] = {
        vehicleId: vehicleKey,
        vehicleName: vehicle ? `${vehicle.number} - ${vehicle.brand} ${vehicle.model}` : `Машина ${vehicleKey}`,
        tripCount: 0,
        distance: 0,
        fuelUsed: 0,
        fuelByNorm: 0
      };
    }

    // Count records as trips
    const recordCount = waybill.records?.length || 0;
    vehicleMap[vehicleKey].tripCount += recordCount;
    totalTripCount += recordCount;

    vehicleMap[vehicleKey].fuelUsed += parseFloat(waybill.total_spent || 0);
    vehicleMap[vehicleKey].fuelByNorm += parseFloat(waybill.required_by_norm || 0);

    // Calculate distance from records - different for fire truck vs passenger car
    if (waybill.records && waybill.records.length > 0) {
      let waybillDistance = 0;
      
      // Check if this is a fire truck or passenger car by checking record fields
      const firstRecord = waybill.records[0];
      const isFireTruck = firstRecord.hasOwnProperty('distance_km');
      
      if (isFireTruck) {
        // Fire truck: sum distance_km from all records
        waybillDistance = waybill.records.reduce((sum, record) => {
          return sum + (record.distance_km || 0);
        }, 0);
      } else {
        // Passenger car: sum (distance_city_km + distance_area_km) from all records
        waybillDistance = waybill.records.reduce((sum, record) => {
          return sum + ((record.distance_city_km || 0) + (record.distance_area_km || 0));
        }, 0);
      }
      
      vehicleMap[vehicleKey].distance += waybillDistance;
      totalDistance += waybillDistance;
    }

    totalFuelUsed += parseFloat(waybill.total_spent || 0);
    totalFuelByNorm += parseFloat(waybill.required_by_norm || 0);

    // Aggregate by driver
    const driverId = waybill.driver;
    // Use driver_full_name from API response, or fallback to searching in drivers_data
    const driver = drivers_data.value.find(d => d.id === driverId);
    const driverFullName = waybill.driver_full_name || (driver ? `${driver.name} ${driver.last_name}`.trim() : `Водитель ${driverId}`);
    
    if (!driverMap[driverId]) {
      driverMap[driverId] = {
        driverId: driverId,
        driverName: driverFullName,
        tripCount: 0,
        distance: 0,
        fuelUsed: 0,
        fuelByNorm: 0
      };
    }
    driverMap[driverId].tripCount += recordCount;
    driverMap[driverId].fuelUsed += parseFloat(waybill.total_spent || 0);
    driverMap[driverId].fuelByNorm += parseFloat(waybill.required_by_norm || 0);
    driverMap[driverId].distance += vehicleMap[vehicleKey].distance;
    
    console.log(`[DEBUG] Driver ${driverId} (${driverFullName}):`, {
      tripCount: recordCount,
      fuelUsed: driverMap[driverId].fuelUsed,
      fuelByNorm: driverMap[driverId].fuelByNorm,
      difference: driverMap[driverId].fuelUsed - driverMap[driverId].fuelByNorm
    });
  });

  const dailyFuel = Object.entries(dailyMap)
    .map(([date, data]) => ({ date, fuel: data.fuelUsed, norm: data.fuelByNorm }))
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  const summaryByVehicle = Object.values(vehicleMap).sort((a, b) => b.fuelUsed - a.fuelUsed);
  const summaryByDriver = Object.values(driverMap).sort((a, b) => b.fuelUsed - a.fuelUsed);

  analytics.value = {
    totalFuelUsed,
    totalFuelByNorm,
    totalDistance,
    tripCount: totalTripCount,
    dailyFuel,
    summaryByVehicle,
    summaryByDriver
  };
};
</script>
