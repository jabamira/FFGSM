<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Нормы для пожарных автомобилей</h2>
      
      <!-- Single White Block: Filters + Tables -->
      <div class="bg-white rounded shadow p-6 mb-16">
        <!-- Filters -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 ">
          <div>
            <SelectInput
              v-model="filterCar"
              label="Фильтр по автомобилю"
              :options="carsFilterOptions"
              placeholder="Все автомобили"
            />
          </div>
          <div>
            <SelectInput
              v-model="filterSeason"
              label="Фильтр по сезону"
              :options="[
                { value: '', label: 'Все сезоны' },
                { value: 'summer', label: 'Лето' },
                { value: 'winter', label: 'Зима' }
              ]"
              placeholder="Все сезоны"
            />
          </div>
        </div>

        <!-- Three Tables in One Row -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Table 1: Norms Fuel Consumption (NormsFireTruck) -->
          <div>
            <div class="px-0 py-2 font-semibold mb-4" :style="{ color: palette.dark }">
              Нормы расхода топлива пожарных
            </div>
            <DataTable
              :data="filteredFuelNorms"
              :columns="fuelNormsColumns"
            >
              <template #cell-car_number="{ row }">
                {{ getCar(row.car)?.number }}
              </template>
              <template #cell-km_norm="{ row }">
                {{ parseFloat(row.km_norm).toFixed(3) }}
              </template>
              <template #cell-with_pump_norm="{ row }">
                {{ parseFloat(row.with_pump_norm).toFixed(3) }}
              </template>
              <template #cell-without_pump_norm="{ row }">
                {{ parseFloat(row.without_pump_norm).toFixed(3) }}
              </template>
            </DataTable>
          </div>

          <!-- Table 2: Operating Hours Norms (NormsOperatingHoursFireTruck) -->
          <div>
            <div class="px-0 py-2 font-semibold mb-4" :style="{ color: palette.dark }">
              Коэффициенты моточасов
            </div>
            <DataTable
              :data="filteredOperatingHoursNorms"
              :columns="operatingHoursNormsColumns"
            >
              <template #cell-car_number="{ row }">
                {{ getCar(row.car)?.number }}
              </template>
              <template #cell-km_norm="{ row }">
                {{ parseFloat(row.km_norm).toFixed(4) }}
              </template>
              <template #cell-with_pump_norm="{ row }">
                {{ parseFloat(row.with_pump_norm).toFixed(4) }}
              </template>
              <template #cell-without_pump_norm="{ row }">
                {{ parseFloat(row.without_pump_norm).toFixed(4) }}
              </template>
            </DataTable>
          </div>

          <!-- Table 3: Technical Maintenance Norms (NormsTechnicalMaintenance) -->
          <div>
            <div class="px-0 py-2 font-semibold mb-4" :style="{ color: palette.dark }">
              Техническое обслуживание
            </div>
            <DataTable
              :data="filteredTechnicalNorms"
              :columns="technicalNormsColumns"
            >
              <template #cell-car_number="{ row }">
                {{ getCar(row.fire_truck)?.number }}
              </template>
              <template #cell-maintenance_type="{ row }">
                {{ row.maintenance_type }}
              </template>
              <template #cell-norm="{ row }">
                {{ parseFloat(row.norm).toFixed(3) }}
              </template>
            </DataTable>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { palette, SelectInput, DataTable } from '../components/ui/importUi';
import NavigationMenu from '../components/NavigationMenu.vue';
import axios from 'axios';

const auth = useAuthStore();

// Data
const fuelNorms = ref([]);
const operatingHoursNorms = ref([]);
const technicalNorms = ref([]);
const fireTrucks = ref([]);

// Filters
const filterCar = ref('');
const filterSeason = ref('');

// Computed
const carsFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все автомобили' },
    ...fireTrucks.value.map(truck => ({
      value: truck.id,
      label: `${truck.number} - ${truck.brand} ${truck.model}`
    }))
  ];
});

const filteredFuelNorms = computed(() => {
  let filtered = fuelNorms.value;

  if (filterCar.value) {
    filtered = filtered.filter(n => n.car === parseInt(filterCar.value));
  }

  if (filterSeason.value) {
    filtered = filtered.filter(n => n.season === filterSeason.value);
  }

  return filtered;
});

const filteredOperatingHoursNorms = computed(() => {
  let filtered = operatingHoursNorms.value;

  if (filterCar.value) {
    filtered = filtered.filter(n => n.car === parseInt(filterCar.value));
  }

  return filtered;
});

const filteredTechnicalNorms = computed(() => {
  let filtered = technicalNorms.value;

  if (filterCar.value) {
    filtered = filtered.filter(n => n.fire_truck === parseInt(filterCar.value));
  }

  return filtered;
});

// Columns definitions
const fuelNormsColumns = [
  { key: 'car_number', label: 'Машина' },
  { key: 'km_norm', label: 'Норма л/км' },
  { key: 'with_pump_norm', label: 'Норма с насосом, л/мин' },
  { key: 'without_pump_norm', label: 'Норма без насоса, л/мин' }
];

const operatingHoursNormsColumns = [
  { key: 'car_number', label: 'Машина' },
  { key: 'km_norm', label: 'Норма км' },
  { key: 'with_pump_norm', label: 'Норма с насосом' },
  { key: 'without_pump_norm', label: 'Норма без насоса' }
];

const technicalNormsColumns = [
  { key: 'car_number', label: 'Машина' },
  { key: 'maintenance_type', label: 'Вид ТО' },
  { key: 'norm', label: 'Норма' }
];

// Methods
const getCar = (carId) => {
  return fireTrucks.value.find(t => t.id === carId);
};

const fetchFireTrucks = async () => {
  try {
    const response = await axios.get('fire-trucks/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fireTrucks.value = response.data;
  } catch (error) {
    console.error('Error fetching fire trucks:', error);
  }
};

const fetchFuelNorms = async () => {
  try {
    const response = await axios.get('fire-truck-norms/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fuelNorms.value = response.data;
    console.log('FireTruck Fuel Norms loaded:', response.data);
    if (response.data.length > 0) console.log('First fuel norm example:', response.data[0]);
  } catch (error) {
    console.error('Error fetching fuel norms:', error);
  }
};

const fetchOperatingHoursNorms = async () => {
  try {
    const response = await axios.get('fire-truck-operating-hours-norms/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    operatingHoursNorms.value = response.data;
    console.log('FireTruck Operating Hours Norms loaded:', response.data);
    if (response.data.length > 0) console.log('First operating hours example:', response.data[0]);
  } catch (error) {
    console.error('Error fetching operating hours norms:', error);
  }
};

const fetchTechnicalNorms = async () => {
  try {
    const response = await axios.get('technical-maintenance-norms/?fire_truck__isnull=false', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    technicalNorms.value = response.data;
    console.log('Technical Maintenance Norms (Fire Trucks) loaded:', response.data);
    if (response.data.length > 0) console.log('First technical norm example:', response.data[0]);
  } catch (error) {
    console.error('Error fetching technical norms:', error);
  }
};

onMounted(async () => {
  await Promise.all([
    fetchFireTrucks(),
    fetchFuelNorms(),
    fetchOperatingHoursNorms(),
    fetchTechnicalNorms()
  ]);
});
</script>

<style scoped>
/* Normalize table header heights for consistent appearance */
:deep(table thead tr) {
  height: 60px;
}

:deep(table thead tr th) {
  height: 105px !important;
  padding: 0.75rem 1rem !important;
  vertical-align: middle;
}

:deep(table thead tr th > div) {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
  


