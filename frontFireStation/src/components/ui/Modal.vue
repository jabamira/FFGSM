<template>
  <teleport to="body">
    <transition name="modal">
      <div 
        v-if="isOpen" 
        class="fixed inset-0 flex items-center justify-center"
        :style="{ 
          backgroundColor: 'rgba(0, 0, 0, 0.35)',
          zIndex: isErrorModal ? 200 : 50
        }"
        @mousedown.self="closeModal"
      >
        <div 
          class="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[800px] overflow-y-auto modal-scrollbar"
          :style="{ zIndex: isErrorModal ? 201 : 51 }"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-12 py-4 border-b" :style="{ borderColor: palette.light }">
            <h2 class="text-lg font-semibold" :style="{ color: palette.dark }">{{ title }}</h2>
            <button
              @click="closeModal"
              class="text-xl font-bold"
              :style="{ color: palette.medium }"
            >
              ✕
            </button>
          </div>

          <!-- Body -->
          <div class="px-12 py-4 overflow-y-auto">
            <slot />
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-end gap-3 px-12 py-4 border-t" :style="{ borderColor: palette.light, backgroundColor: `${palette.light}20` }">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
import { ref } from 'vue';
import { theme, palette } from './theme';

export default {
  name: 'Modal',
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    title: {
      type: String,
      default: 'Modal',
    },
  },
  emits: ['close'],
  setup(props, { emit, expose }) {
    const isErrorModal = ref(false);
    const closeModal = () => emit('close');

    return {
      theme,
      palette,
      closeModal,
      isErrorModal,
    };
  },
};
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-to,
.modal-leave-from {
  opacity: 1;
}

/* Стилизация скроллбара модального окна */
.modal-scrollbar::-webkit-scrollbar {
  width: 10px;
}

.modal-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}

.modal-scrollbar::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 10px;
  border: 2px solid #f1f5f9;
  transition: background 0.2s ease;
}

.modal-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
</style>
