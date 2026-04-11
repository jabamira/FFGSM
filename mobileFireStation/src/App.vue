<template>
  <ion-app>
    <ion-router-outlet />
    <ConsoleDisplay />
  </ion-app>
</template>

<script setup>
import { IonApp, IonRouterOutlet } from '@ionic/vue'
import ConsoleDisplay from './components/ConsoleDisplay.vue'
</script>

<style>
#app,
html,
body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

ion-app {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

ion-router-outlet {
  flex: 1;
  overflow: hidden;
}
</style>
