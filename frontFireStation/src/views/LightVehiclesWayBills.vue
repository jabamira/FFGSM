<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Путевые листы легковых автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <p :style="{ color: palette.medium }">Здесь будет список путевых листов легковых автомобилей...</p>
        <Alert 
          type="info"
          message="Раздел в разработке. Скоро здесь появится управление путевыми листами."
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { palette, Alert } from '../components/ui/importUi';
import NavigationMenu from '../components/NavigationMenu.vue';
</script>
