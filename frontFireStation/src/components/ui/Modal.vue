<template>
  <teleport to="body">
    <transition name="modal">
      <div v-if="isOpen" :class="theme.modal.overlay" @click.self="closeModal">
        <div :class="theme.modal.content">
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b" :style="{ borderColor: palette.light }">
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
          <div class="px-6 py-4 overflow-y-auto">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="flex items-center justify-end gap-3 px-6 py-4 border-t" :style="{ borderColor: palette.light, backgroundColor: `${palette.light}20` }">
            <slot name="footer" />
          </div>
          <div v-else class="flex items-center justify-end gap-3 px-6 py-4 border-t" :style="{ borderColor: palette.light, backgroundColor: `${palette.light}20` }">
            <button
              @click="closeModal"
              class="px-4 py-2 rounded-lg transition"
              :style="{ color: palette.dark, backgroundColor: `${palette.light}40` }"
            >
              Close
            </button>
            <button
              v-if="!hideConfirm"
              @click="confirmAction"
              class="px-4 py-2 text-white rounded-lg transition"
              :style="{ backgroundColor: palette.primary }"
            >
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
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
    confirmLabel: {
      type: String,
      default: 'Confirm',
    },
    hideConfirm: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const closeModal = () => emit('close');
    const confirmAction = () => emit('confirm');

    return {
      theme,
      palette,
      closeModal,
      confirmAction,
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
</style>
