<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useTripStore } from '../stores/trip'
import { palette } from '../components/ui/theme'
import { IonFooter, IonIcon } from '@ionic/vue'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()
const tripStore = useTripStore()

const hasActiveTrip = computed(() => tripStore.hasActiveTrip)

const handleNavigation = async (path, event) => {
  // Blur the button to remove focus before transition
  event.target.blur?.()
  await router.push(path)
}

const handleWaybillsClick = async (event) => {
  // Если есть активная поездка, переходим на страницу поездки
  if (hasActiveTrip.value) {
    await handleNavigation('/trip/active', event)
  } else {
    await handleNavigation('/waybills', event)
  }
}

const getWaybillsLabel = () => {
  return hasActiveTrip.value ? 'Поездка' : 'Путевые листы'
}

const isWaybillsActive = () => {
  if (hasActiveTrip.value) {
    return route.path === '/trip/active'
  }
  return route.path === '/waybills'
}
</script>

<template>
  <div class="footer-wrapper">
    <ion-footer>
      <div class="flex justify-around w-full px-2 py-1">
        <button
          @click="handleWaybillsClick($event)"
          class="flex-1 flex flex-col items-center gap-1 text-sm font-semibold transition"
          :style="{ color: isWaybillsActive() ? palette.primary : palette.medium }"
        >
          <!-- Trip icon image or default icon -->
          <div v-if="hasActiveTrip" style="width: 24px; height: 24px;">
            <img src="@/assets/free-icon-car-trip.png" alt="Trip" style="width: 100%; height: 100%; object-fit: contain;" />
          </div>
          <ion-icon v-else name="document-outline" style="font-size: 24px;"></ion-icon>
          <span class="text-xs">{{ getWaybillsLabel() }}</span>
        </button>
        <button
          @click="handleNavigation('/settings', $event)"
          class="flex-1 flex flex-col items-center gap-1 text-sm font-semibold transition"
          :style="{ color: route.path === '/settings' ? palette.primary : palette.medium }"
        >
          <ion-icon name="settings-outline" style="font-size: 24px;"></ion-icon>
          <span class="text-xs">Настройки</span>
        </button>
      </div>
    </ion-footer>
  </div>
</template>

<style scoped>
.footer-wrapper {
  width: 100%;
  border-top: 1px solid #e5e7eb;
  background-color: #ffffff;
}

:deep(ion-footer) {
  --padding-bottom: 0;
  --padding-end: 0;
  --padding-start: 0;
  --padding-top: 0;
  background-color: #ffffff;
  box-shadow: none !important;
}

button {
  cursor: pointer;
  padding: 8px;
}
</style>
