<template>
  <div>
    <NavigationMenu />
    <div class="p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl font-semibold mb-4" :style="{ color: palette.dark }">Нормы для пожарных автомобилей</h2>
      <div class="bg-white rounded shadow p-6" :style="{ borderColor: palette.light }">
        <p :style="{ color: palette.medium }">Здесь будут нормы расхода топлива для пожарных автомобилей...</p>
        <Alert 
          type="info"
          message="Раздел в разработке. Скоро здесь появится управление нормами."
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { palette, Alert } from '../components/ui/importUi';
import NavigationMenu from '../components/NavigationMenu.vue';
</script>
