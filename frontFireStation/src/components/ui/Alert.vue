<template>
  <div :style="alertStyle" class="p-4 rounded-lg" role="alert">
    <div class="flex items-start gap-3">
      <div v-if="icon" class="mt-0.5">
        <span v-if="type === 'success'" class="text-2xl">✓</span>
        <span v-else-if="type === 'error'" class="text-2xl">✕</span>
        <span v-else-if="type === 'warning'" class="text-2xl">⚠</span>
        <span v-else class="text-2xl">ℹ</span>
      </div>
      <div class="flex-1">
        <h3 v-if="title" class="font-semibold">{{ title }}</h3>
        <p>{{ message }}</p>
      </div>
      <button
        v-if="closeable"
        @click="$emit('close')"
        class="text-xl font-bold"
        :style="{ color: alertColor }"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { palette } from './theme';

export default {
  name: 'Alert',
  props: {
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value),
    },
    title: {
      type: String,
      default: '',
    },
    message: {
      type: String,
      required: true,
    },
    closeable: {
      type: Boolean,
      default: true,
    },
    icon: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['close'],
  setup(props) {
    const typeConfig = {
      success: { bg: `${palette.success}15`, text: palette.success },
      error: { bg: `${palette.error}15`, text: palette.error },
      warning: { bg: `${palette.warning}15`, text: palette.warning },
      info: { bg: `${palette.primary}15`, text: palette.primary },
    };

    const alertStyle = computed(() => {
      const config = typeConfig[props.type];
      return {
        backgroundColor: config.bg,
        color: config.text,
        border: `1px solid ${config.text}30`,
      };
    });

    const alertColor = computed(() => typeConfig[props.type].text);

    return { alertStyle, alertColor };
  },
};
</script>
