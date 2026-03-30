<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-[80%] mx-auto pb-24">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Нормы для легковых автомобилей</h2>
      
      <!-- Single White Block: Filters + Tables -->
      <div class="bg-white rounded shadow p-6 mb-16">
        <!-- Filters -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
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
          <!-- Table 1: Norms Fuel Consumption (NormsPassengerCars) -->
          <div>
            <div class="px-0 py-2 font-semibold mb-4" :style="{ color: palette.dark }">
              Нормы расхода топлива
            </div>
            <DataTable
              :data="filteredFuelNorms"
              :columns="fuelNormsColumns"
            >
              <template #cell-car_number="{ row }">
                {{ getCar(row.car)?.number }}
              </template>
              <template #cell-city_norm="{ row }">
                {{ parseFloat(row.city_norm).toFixed(3) }}
              </template>
              <template #cell-area_norm="{ row }">
                {{ parseFloat(row.area_norm).toFixed(3) }}
              </template>
            </DataTable>
          </div>

          <!-- Table 2: Operating Hours Norms (NormsOperatingHoursPassengerCar) -->
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
              <template #cell-city_norm="{ row }">
                {{ parseFloat(row.city_norm).toFixed(4) }}
              </template>
              <template #cell-area_norm="{ row }">
                {{ parseFloat(row.area_norm).toFixed(4) }}
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
                {{ getCar(row.passenger_car)?.number }}
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
const passengerCars = ref([]);

// Filters
const filterCar = ref('');
const filterSeason = ref('');

// Computed
const carsFilterOptions = computed(() => {
  return [
    { value: '', label: 'Все автомобили' },
    ...passengerCars.value.map(car => ({
      value: car.id,
      label: `${car.number} - ${car.brand} ${car.model}`
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
    filtered = filtered.filter(n => n.passenger_car === parseInt(filterCar.value));
  }

  return filtered;
});

// Columns definitions
const fuelNormsColumns = [
  { key: 'car_number', label: 'Машина' },
  { key: 'city_norm', label: 'Город' },
  { key: 'area_norm', label: 'Трасса' }
];

const operatingHoursNormsColumns = [
  { key: 'car_number', label: 'Машина' },
  { key: 'city_norm', label: 'Город' },
  { key: 'area_norm', label: 'Трасса' }
];

const technicalNormsColumns = [
  { key: 'car_number', label: 'Машина' },
  { key: 'maintenance_type', label: 'Вид ТО' },
  { key: 'norm', label: 'Норма' }
];

// Methods
const getCar = (carId) => {
  return passengerCars.value.find(c => c.id === carId);
};

const fetchPassengerCars = async () => {
  try {
    const response = await axios.get('passenger-cars/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    passengerCars.value = response.data;
  } catch (error) {
    console.error('Error fetching passenger cars:', error);
  }
};

const fetchFuelNorms = async () => {
  try {
    const response = await axios.get('passenger-car-norms/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    fuelNorms.value = response.data;
    console.log('Passenger Car Fuel Norms loaded:', response.data);
    if (response.data.length > 0) console.log('First fuel norm example:', response.data[0]);
  } catch (error) {
    console.error('Error fetching fuel norms:', error);
  }
};

const fetchOperatingHoursNorms = async () => {
  try {
    const response = await axios.get('passenger-car-operating-hours-norms/', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    operatingHoursNorms.value = response.data;
    console.log('Passenger Car Operating Hours Norms loaded:', response.data);
    if (response.data.length > 0) console.log('First operating hours example:', response.data[0]);
  } catch (error) {
    console.error('Error fetching operating hours norms:', error);
  }
};

const fetchTechnicalNorms = async () => {
  try {
    const response = await axios.get('technical-maintenance-norms/?passenger_car__isnull=false', {
      headers: { Authorization: `Bearer ${auth.access}` }
    });
    technicalNorms.value = response.data;
    console.log('Technical Maintenance Norms (Passenger Cars) loaded:', response.data);
    if (response.data.length > 0) console.log('First technical norm example:', response.data[0]);
  } catch (error) {
    console.error('Error fetching technical norms:', error);
  }
};

onMounted(async () => {
  await Promise.all([
    fetchPassengerCars(),
    fetchFuelNorms(),
    fetchOperatingHoursNorms(),
    fetchTechnicalNorms()
  ]);
});
</script>


