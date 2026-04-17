<template>
  <transition name="slide-down">
    <div 
      v-if="isVisible"
      class="fixed top-4 right-4 z-40 flex items-center gap-2 px-3 py-2 rounded-lg shadow-md"
      style="background-color: #9ca3af; color: #ffffff;"
    >
      <div class="w-2 h-2 rounded-full" style="background-color: #ffffff;"></div>
      <span class="text-xs font-medium">
        {{ isOnline ? 'Онлайн' : 'Офлайн' }}
      </span>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const isOnline = ref(navigator.onLine)
const isVisible = ref(false)
let hideTimeout = null

function updateOnlineStatus() {
  isOnline.value = navigator.onLine
  isVisible.value = true
  
  if (hideTimeout) clearTimeout(hideTimeout)
  hideTimeout = setTimeout(() => {
    isVisible.value = false
  }, 3000)

  if (!isOnline.value) {
    console.warn('[OnlineStatus] Lost connection to server')
  } else {
    console.log('[OnlineStatus] Connected to server')
  }
}

onMounted(() => {
  isVisible.value = true
  if (hideTimeout) clearTimeout(hideTimeout)
  hideTimeout = setTimeout(() => {
    isVisible.value = false
  }, 3000)

  window.addEventListener('online', updateOnlineStatus)
  window.addEventListener('offline', updateOnlineStatus)
})

onUnmounted(() => {
  window.removeEventListener('online', updateOnlineStatus)
  window.removeEventListener('offline', updateOnlineStatus)
  if (hideTimeout) {
    clearTimeout(hideTimeout)
  }
})
</script>

<style scoped>
@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(-100%);
    opacity: 0;
  }
}

.slide-down-enter-active {
  animation: slideDown 0.3s ease;
}

.slide-down-leave-active {
  animation: slideUp 0.3s ease;
}
</style>
