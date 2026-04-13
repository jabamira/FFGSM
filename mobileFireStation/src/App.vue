<template>
  <ion-app>
    <ion-router-outlet />
    <ConsoleDisplay />
  </ion-app>
</template>

<script setup>
import { IonApp, IonRouterOutlet } from '@ionic/vue'
import { onMounted } from 'vue'
import ConsoleDisplay from './components/ConsoleDisplay.vue'
import { initStatusBar } from './utils/statusBar'

// Инициализируем статус-бар при загрузке приложения
onMounted(() => {
  initStatusBar()
})
</script>

<style>
#app,
html,
body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
}

ion-app {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
}

ion-router-outlet {
  flex: 1;
  overflow: hidden;
}
</style>
