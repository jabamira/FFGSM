<template>
  <button
    :style="buttonStyle"
  :class="buttonClass"
    :disabled="disabled || loading"
    @click="$emit('click')"
  >
    <span v-if="loading" class="inline-block mr-2">
      <svg
        class="animate-spin h-4 w-4 inline"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </span>
    <slot>{{ label }}</slot>
  </button>
</template>

<script>
import { computed } from 'vue';
import { palette } from './theme';

export default {
  name: 'Button',
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'danger', 'success', 'outline', 'ghost'].includes(value),
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value),
    },
    label: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    fullWidth: {
      type: Boolean,
      default: false,
    },
    rounded: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['click'],
setup(props) {

  const sizeClasses = {
    xs: 'px-2 py-1 text-xs min-w-[60px]',
    sm: 'px-3 py-1.5 text-sm min-w-[80px]',
    md: 'px-4 py-2 text-base min-w-[100px]',
    lg: 'px-6 py-3 text-lg min-w-[140px]',
    xl: 'px-8 py-4 text-xl min-w-[180px]',
  };

const variantClasses = {
  primary: 'bg-primary text-white hover:bg-primary/85 hover:shadow transition-colors transition-shadow duration-200',
  secondary: 'bg-secondary text-white hover:bg-secondary/85 hover:shadow transition-colors transition-shadow duration-200',
  danger: 'bg-error text-white hover:bg-error/85 hover:shadow transition-colors transition-shadow duration-200',
  success: 'bg-success text-white hover:bg-success/85 hover:shadow transition-colors transition-shadow duration-200',
  outline: 'border-2 border-primary text-primary hover:bg-primary/5 hover:shadow transition-colors transition-shadow duration-200',
  ghost: 'text-dark hover:bg-black/10 hover:shadow transition-colors transition-shadow duration-200',
};


const buttonClass = computed(() => [
  'inline-flex items-center justify-center font-medium rounded-lg', // базовые классы
  sizeClasses[props.size],
  variantClasses[props.variant],
  props.rounded && 'rounded-full',
  props.fullWidth && 'w-full',
  props.disabled && 'opacity-60 cursor-not-allowed',
  !props.disabled && 'hover:shadow-intense', // сильная тень при наведении
]);

  
  const buttonStyle = computed(() => {
    const variant = variantClasses[props.variant]; // для bg/text, если нужно palette
    return {}; // пусто, теперь текст не дергается
  });

  return { buttonClass, buttonStyle };
}

};
</script>
