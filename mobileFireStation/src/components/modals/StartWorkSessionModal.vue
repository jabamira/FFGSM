<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Overlay -->
    <div 
      class="absolute inset-0 bg-black/50"
      @click="$emit('close')"
    ></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6 space-y-6">
      <!-- Title -->
      <div class="text-center">
        <h2 class="text-xl font-bold" :style="{ color: palette.dark }">
          Начать работу?
        </h2>
      </div>

      <!-- Mode Display -->
      <div class="p-4 rounded-lg" :style="{ backgroundColor: '#ffffff', borderLeft: `4px solid ${palette.primary}` }">
        <p class="text-xs font-medium" :style="{ color: palette.medium }">Режим</p>
        <p class="text-lg font-bold mt-2" :style="{ color: palette.dark }">
          {{ modeLabel }}
        </p>
      </div>

      <!-- Info Box -->
      <div class="p-3 rounded-lg bg-blue-50 border-l-4" :style="{ borderColor: palette.primary }">
        <p class="text-xs font-medium" :style="{ color: palette.primary }">ℹ️ Информация</p>
        <p class="text-xs mt-1" :style="{ color: palette.dark }">
          Убедитесь, что вы готовы начать работу в режиме <strong>{{ modeLabel }}</strong>. Время будет отсчитываться с момента начала.
        </p>
      </div>

      <!-- Buttons -->
      <div class="flex gap-3">
        <Button
          label="Отмена"
          variant="secondary"
          expand="block"
          @click="$emit('close')"
          :disabled="isLoading"
        />
        <Button
          label="Начать работу"
          variant="primary"
          expand="block"
          :is-loading="isLoading"
          loading-text="Запуск..."
          @click="$emit('confirm')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { palette, Button } from '../ui/importUi'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirm', 'close'])

const modeLabel = computed(() => {
  const modes = {
    'with_pump': 'С насосом',
    'without_pump': 'Без насоса'
  }
  return modes[props.mode] || props.mode
})
</script>

<style scoped>
.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.flex.gap-3 > * + * {
  margin-left: 0.75rem;
}
</style>
