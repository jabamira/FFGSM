<template>
  <ion-modal 
    :is-open="isOpen" 
    @didDismiss="$emit('close')"
    :backdrop-dismiss="false"
  >
    <ion-header :translucent="true">
      <ion-toolbar :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)' }">
        <ion-title :style="{ color: palette.dark }">Подтвердить заправку</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="$emit('close')">
            <ion-icon slot="icon-only" :icon="close" :style="{ color: palette.dark }"></ion-icon>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="space-y-4">
        <!-- Amount Display -->
        <div class="p-4 rounded-lg" :style="{ backgroundColor: '#ffffff', borderLeft: `4px solid ${palette.primary}` }">
          <p class="text-xs font-medium" :style="{ color: palette.medium }">Количество заправки</p>
          <p class="text-3xl font-bold mt-2" :style="{ color: palette.primary }">
            {{ amount.toFixed(1) }} л
          </p>
        </div>

        <!-- Info Box -->
        <div class="p-4 rounded-lg bg-blue-50 border-l-4" :style="{ borderColor: palette.primary }">
          <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
          <p class="text-xs mt-2" :style="{ color: palette.dark }">
            Убедитесь, что введено корректное количество литров. После подтверждения это значение будет зафиксировано и перенесено на страницу завершения поездки.
          </p>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 mt-6">
          <Button
            label="Отмена"
            variant="secondary"
            expand="block"
            @click="$emit('close')"
            :disabled="isLoading"
          />
          <Button
            label="Подтвердить"
            variant="primary"
            expand="block"
            :is-loading="isLoading"
            loading-text="Сохранение..."
            @click="$emit('confirm')"
          />
        </div>
      </div>
    </ion-content>
  </ion-modal>
</template>

<script setup>
import { close } from 'ionicons/icons'
import { IonModal, IonHeader, IonToolbar, IonTitle, IonButtons, IonButton, IonIcon, IonContent } from '@ionic/vue'
import { palette, Button } from '../ui/importUi'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  amount: {
    type: Number,
    default: 0
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirm', 'close'])
</script>

<style scoped>
.space-y-4 > * + * {
  margin-top: 1rem;
}
</style>
