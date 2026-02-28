<template>
  <span :style="badgeStyle" class="inline-block rounded-full font-medium">
    <slot>{{ label }}</slot>
  </span>
</template>

<script>
import { computed } from 'vue';
import { palette } from './theme';

export default {
  name: 'Badge',
  props: {
    type: {
      type: String,
      default: 'default',
      validator: (value) =>
        ['default', 'success', 'error', 'warning', 'info', 'primary'].includes(value),
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg'].includes(value),
    },
    label: {
      type: String,
      default: '',
    },
    outline: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const typeConfig = {
      default: { bg: palette.light, text: 'white' },
      success: { bg: palette.success, text: 'white' },
      error: { bg: palette.error, text: 'white' },
      warning: { bg: palette.warning, text: 'white' },
      info: { bg: palette.primary, text: 'white' },
      primary: { bg: palette.primary, text: 'white' },
    };

    const sizeClasses = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-3 py-1 text-sm',
      lg: 'px-4 py-1.5 text-base',
    };

    const badgeStyle = computed(() => {
      const config = typeConfig[props.type];
      const sizeClass = sizeClasses[props.size];

      if (props.outline) {
        return {
          backgroundColor: 'transparent',
          color: config.bg,
          border: `1px solid ${config.bg}`,
          ...parseSize(sizeClass),
        };
      }

      return {
        backgroundColor: config.bg,
        color: config.text,
        ...parseSize(sizeClass),
      };
    });

    const parseSize = (sizeClass) => {
      const [padding, fontSize] = sizeClass.split(' ');
      return {
        padding: convertPadding(padding),
        fontSize: convertFontSize(fontSize),
      };
    };

    const convertPadding = (p) => {
      const map = {
        'px-2': '0.5rem 0.5rem',
        'py-0.5': '0.125rem',
        'px-3': '0.75rem',
        'py-1': '0.25rem',
        'px-4': '1rem',
        'py-1.5': '0.375rem',
      };
      return map[p] || p;
    };

    const convertFontSize = (f) => {
      const map = {
        'text-xs': '0.75rem',
        'text-sm': '0.875rem',
        'text-base': '1rem',
      };
      return map[f] || f;
    };

    return { badgeStyle };
  },
};
</script>
