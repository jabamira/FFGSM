<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Overlay -->
    <div 
      class="absolute inset-0 bg-black/50"
      @click="closeModal"
    ></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6 space-y-6">
      <!-- Icon -->
      <div class="flex justify-center">
        <div class="flex items-center justify-center w-16 h-16 rounded-full" :style="{ backgroundColor: palette.primary + '20' }">
          <!-- Using trip icon image from resources -->
          <img src="@/assets/free-icon-car-trip.png" alt="Trip" style="width: 40px; height: 40px; object-fit: contain;" />
        </div>
      </div>

      <!-- Title -->
      <div class="text-center">
        <h2 class="text-xl font-bold" :style="{ color: palette.dark }">
          Начать поездку?
        </h2>
      </div>

      <!-- Trip Details -->
      <div class="space-y-3 p-4 rounded-lg" :style="{ backgroundColor: palette.light + '10' }">
        <!-- Vehicle -->
        <div>
          <p class="text-xs font-medium" :style="{ color: palette.medium }">Машина</p>
          <p class="text-sm font-semibold" :style="{ color: palette.dark }">
            {{ vehicleInfo.brand && vehicleInfo.model ? `${vehicleInfo.brand} ${vehicleInfo.model}` : vehicleInfo.name }}
          </p>
          <p class="text-xs" :style="{ color: palette.medium }">{{ vehicleInfo.number }}</p>
        </div>

        <!-- Date -->
        <div class="flex justify-between items-start">
          <div>
            <p class="text-xs font-medium" :style="{ color: palette.medium }">Дата</p>
            <p class="text-sm font-semibold" :style="{ color: palette.dark }">{{ formatDate(tripData.date) }}</p>
          </div>
          <div>
            <p class="text-xs font-medium" :style="{ color: palette.medium }">Время</p>
            <p class="text-sm font-semibold" :style="{ color: palette.dark }">{{ tripData.time }}</p>
          </div>
        </div>

        <!-- Trip Purpose (if provided) -->
        <div v-if="tripData.tripPurpose">
          <p class="text-xs font-medium" :style="{ color: palette.medium }">Цель выезда</p>
          <p class="text-sm" :style="{ color: palette.dark }">{{ tripData.tripPurpose }}</p>
        </div>

        <!-- Trip Route (if provided) -->
        <div v-if="tripData.tripRoute">
          <p class="text-xs font-medium" :style="{ color: palette.medium }">Маршрут движения</p>
          <p class="text-sm" :style="{ color: palette.dark }">{{ tripData.tripRoute }}</p>
        </div>
      </div>

      <!-- Warning -->
      <div class="p-3 rounded-lg bg-blue-50 border-l-4" :style="{ borderColor: palette.primary }">
        <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
        <p class="text-xs mt-1" :style="{ color: palette.dark }">
          Убедитесь, что все данные верны. После начала поездки данные будут зафиксированы.
        </p>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <Button
          label="Отмена"
          variant="secondary"
          @click="closeModal"
          expand="block"
        />
        <Button
          :label="isLoading ? 'Загрузка...' : 'Начать поездку'"
          variant="primary"
          :disabled="isLoading"
          :is-loading="isLoading"
          loading-text="Загрузка..."
          @click="confirmTrip"
          expand="block"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IonSpinner } from '@ionic/vue'
import { palette, Button } from '../ui/importUi'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  vehicleInfo: {
    type: Object,
    default: () => ({
      name: '',
      number: '',
      brand: '',
      model: '',
      vehicleType: ''
    })
  },
  tripData: {
    type: Object,
    default: () => ({
      date: new Date().toISOString().split('T')[0],
      time: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
      tripPurpose: '',
      tripRoute: ''
    })
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['confirm', 'close'])

const isFireTruck = computed(() => props.vehicleInfo.vehicleType === 'fire_truck')

const closeModal = () => {
  emit('close')
}

const confirmTrip = () => {
  emit('confirm')
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

defineExpose({
  closeModal
})
</script>

<style scoped>
ion-spinner {
  display: inline-block;
}
</style>
