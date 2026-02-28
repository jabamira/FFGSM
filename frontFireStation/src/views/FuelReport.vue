<template>
  <div class="p-6 max-w-6xl mx-auto">
    <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Отчёт по ГСМ — заполнение механиком</h2>

    <p class="text-sm mb-4" :style="{ color: palette.medium }">Заполните поля ниже. Вводимые поля — редактируемые, вычисляемые — выделены цветом.</p>

    <div class="mb-4 flex items-center gap-4">
      <div class="p-2 bg-white border rounded shadow-sm" :style="{ borderColor: palette.light }">
        <strong :style="{ color: palette.dark }">Вводимые поля</strong>
        <div class="text-xs" :style="{ color: palette.medium }">(механик заполняет)</div>
      </div>
      <div class="p-2 rounded shadow-sm" :style="{ backgroundColor: palette.success + '15', border: '1px solid ' + palette.success }">
        <strong :style="{ color: palette.dark }">Автоматически вычисляемые</strong>
        <div class="text-xs" :style="{ color: palette.medium }">(считается автоматически)</div>
      </div>
    </div>

    <div class="bg-white rounded shadow p-4" :style="{ borderColor: palette.light }">
      <form @submit.prevent="addRecord" class="space-y-2">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <TextInput v-model="newRecord.date" type="date" label="Дата" />
          <TextInput v-model="newRecord.driver" label="Водитель (ФИО)" placeholder="Иванов Иван" />
          <TextInput v-model.number="newRecord.odometer_after" type="number" label="Одометр (после), км" />
          <TextInput v-model.number="newRecord.fuel_refueled" type="number" label="Заправлено, л" />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <TextInput v-model.number="newRecord.distance_city_km" type="number" label="Пробег город, км" />
          <TextInput v-model.number="newRecord.distance_area_km" type="number" label="Пробег область, км" />
          <SelectInput v-model="newRecord.season" :options="seasonOptions" label="Сезон" />
          <TextInput v-model="newRecord.comment" label="Комментарий" placeholder="необязательно" />
        </div>

        <div class="flex justify-end">
          <Button type="button" @click="addRecord" label="Добавить запись" variant="primary" />
        </div>
      </form>
    </div>

    <div class="mt-6">
      <DataTable :data="records" :columns="columns" :paginate="false">
        <template #cell-odometer_before="{ value }">
          <div :style="{ backgroundColor: palette.success + '10', padding: '6px', borderRadius: '4px', color: palette.dark }">{{ formatNum(value) }}</div>
        </template>

        <template #cell-distance_total_km="{ value }">
          <div :style="{ backgroundColor: palette.success + '10', padding: '6px', borderRadius: '4px', color: palette.dark }">{{ formatNum(value) }}</div>
        </template>

        <template #cell-norm_city="{ value }">
          <div :style="{ backgroundColor: palette.success + '10', padding: '6px', borderRadius: '4px', color: palette.dark }">{{ value.toFixed(3) }}</div>
        </template>

        <template #cell-norm_area="{ value }">
          <div :style="{ backgroundColor: palette.success + '10', padding: '6px', borderRadius: '4px', color: palette.dark }">{{ value.toFixed(3) }}</div>
        </template>

        <template #cell-fuel_used_total="{ value }">
          <div :style="{ backgroundColor: palette.success + '10', padding: '6px', borderRadius: '4px', color: palette.dark }">{{ value.toFixed(3) }}</div>
        </template>

        <template #cell-fuel_on_return="{ value }">
          <div :style="{ backgroundColor: palette.success + '10', padding: '6px', borderRadius: '4px', color: palette.dark }">{{ value.toFixed(3) }}</div>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { TextInput, SelectInput, Button, DataTable, palette } from '../components/ui/importUi';

const defaults = {
  summer: { norm_city: 0.09, norm_area: 0.11 },
  winter: { norm_city: 0.10, norm_area: 0.12 },
};

const seasonOptions = [
  { value: 'summer', label: 'лето' },
  { value: 'winter', label: 'зима' },
];

const records = ref([]);

const newRecord = reactive({
  date: new Date().toISOString().slice(0,10),
  driver: '',
  odometer_after: 0,
  fuel_refueled: 0,
  distance_city_km: 0,
  distance_area_km: 0,
  season: 'summer',
  comment: '',
});

const columns = [
  { key: 'date', label: 'Дата' },
  { key: 'driver', label: 'Водитель' },
  { key: 'odometer_before', label: 'Одометр до' },
  { key: 'odometer_after', label: 'Одометр после' },
  { key: 'distance_total_km', label: 'Пробег (всего)' },
  { key: 'norm_city', label: 'Норма (город)' },
  { key: 'norm_area', label: 'Норма (область)' },
  { key: 'fuel_used_total', label: 'Расход всего, л' },
  { key: 'fuel_refueled', label: 'Заправлено, л' },
  { key: 'fuel_on_return', label: 'На возвращении, л' },
  { key: 'comment', label: 'Комментарий' },
];

function formatNum(v) {
  return Number(v || 0).toFixed(2);
}

function computeFromInput(nr, prevFuelOnReturn, prevOdometer) {
  const norm_city = defaults[nr.season].norm_city;
  const norm_area = defaults[nr.season].norm_area;
  const distance_total_km = Number(nr.distance_city_km || 0) + Number(nr.distance_area_km || 0);
  const fuel_used_city = Number(nr.distance_city_km || 0) * norm_city;
  const fuel_used_area = Number(nr.distance_area_km || 0) * norm_area;
  const fuel_used_total = fuel_used_city + fuel_used_area;
  const fuel_before_departure = prevFuelOnReturn ?? 0;
  const fuel_on_return = Number(fuel_before_departure) - fuel_used_total + Number(nr.fuel_refueled || 0);
  const odometer_before = prevOdometer ?? 0;

  return {
    odometer_before: Number(odometer_before),
    odometer_after: Number(nr.odometer_after || 0),
    distance_total_km,
    norm_city,
    norm_area,
    fuel_used_total,
    fuel_before_departure,
    fuel_on_return,
  };
}

function addRecord() {
  const prev = records.value.length ? records.value[records.value.length-1] : null;
  const prevFuel = prev ? prev.fuel_on_return : 0;
  const prevOdom = prev ? prev.odometer_after : 0;

  const calc = computeFromInput(newRecord, prevFuel, prevOdom);

  records.value.push({
    date: newRecord.date,
    driver: newRecord.driver || '—',
    odometer_before: calc.odometer_before,
    odometer_after: calc.odometer_after,
    distance_total_km: calc.distance_total_km,
    norm_city: calc.norm_city,
    norm_area: calc.norm_area,
    fuel_used_total: calc.fuel_used_total,
    fuel_before_departure: calc.fuel_before_departure,
    fuel_refueled: Number(newRecord.fuel_refueled || 0),
    fuel_on_return: calc.fuel_on_return,
    comment: newRecord.comment || '',
  });

  // Сброс вводимых полей (оставляем дату и сезон)
  newRecord.odometer_after = newRecord.odometer_after;
  newRecord.fuel_refueled = 0;
  newRecord.distance_city_km = 0;
  newRecord.distance_area_km = 0;
  newRecord.comment = '';
}
</script>

<style scoped>
/* минимальная стилизация: DataTable и компоненты используют theme.js */
</style>
