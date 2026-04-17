<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Overlay -->
    <div 
      class="absolute inset-0 bg-black/50"
      @click="closeModal"
    ></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6 space-y-6">
      <!-- Title -->
      <div class="text-center">
        <h2 class="text-xl font-bold" :style="{ color: palette.dark }">
          Завершить сеанс работы?
        </h2>
      </div>

      <!-- Session Info -->
      <div class="space-y-3 p-4 rounded-lg" :style="{ backgroundColor: palette.light + '10' }">
        <div>
          <p class="text-xs font-medium" :style="{ color: palette.medium }">Режим</p>
          <p class="text-sm font-semibold" :style="{ color: palette.dark }">
            {{ mode === 'with_pump' ? 'С насосом' : 'Без насоса' }}
          </p>
        </div>

        <div>
          <p class="text-xs font-medium" :style="{ color: palette.medium }">Время работы</p>
          <p class="text-lg font-bold" :style="{ color: palette.primary }">
            {{ formatTime(duration) }}
          </p>
        </div>
      </div>

      <!-- Info -->
      <div class="p-3 rounded-lg bg-blue-50 border-l-4" :style="{ borderColor: palette.primary }">
        <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
        <p class="text-xs mt-1" :style="{ color: palette.dark }">
          Подтвердите завершение рабочего сеанса. Время будет сохранено.
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
          label="Завершить"
          variant="primary"
          :disabled="isLoading"
          :is-loading="isLoading"
          loading-text="Сохранение..."
          @click="confirmStop"
          expand="block"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { palette, Button } from '../ui/importUi'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'with_pump' // 'with_pump' или 'without_pump'
  },
  duration: {
    type: Number,
    default: 0 // в миллисекундах
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['confirm', 'close'])

const closeModal = () => {
  emit('close')
}

const confirmStop = () => {
  emit('confirm')
}

const formatTime = (ms) => {
  const seconds = Math.floor(ms / 1000)
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}ч ${minutes}м ${secs}с`
  }
  if (minutes > 0) {
    return `${minutes}м ${secs}с`
  }
  return `${secs}с`
}
</script>
