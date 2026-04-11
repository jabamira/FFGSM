<template>
  <button
    v-if="useNativeButton"
    :disabled="disabled || isLoading"
    :type="type"
    class="ion-button-native"
    :style="getButtonStyle()"
    @click="$emit('click')"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <ion-spinner v-if="isLoading" name="crescent"></ion-spinner>
    <span v-if="isLoading">{{ loadingText }}</span>
    <span v-else>{{ label }}</span>
  </button>
  <ion-button
    v-else
    :color="colorMap[variant]"
    :expand="expand"
    :disabled="disabled || isLoading"
    :type="type"
    class="text-base"
  >
    <ion-spinner v-if="isLoading" name="crescent" slot="start"></ion-spinner>
    <span v-if="isLoading">{{ loadingText }}</span>
    <span v-else>{{ label }}</span>
  </ion-button>
</template>

<script setup>
import { IonButton, IonSpinner } from '@ionic/vue'
import { computed } from 'vue'
import { palette } from './theme'

const props = defineProps({
  label: {
    type: String,
    default: 'Button',
  },
  variant: {
    type: String,
    enum: ['primary', 'secondary', 'success', 'danger', 'warning'],
    default: 'primary',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  loadingText: {
    type: String,
    default: 'Загрузка...',
  },
  type: {
    type: String,
    default: 'button',
  },
  expand: {
    type: String,
    enum: ['block', 'full', undefined],
    default: undefined,
  },
  useNativeButton: {
    type: Boolean,
    default: true,
  },
})

const colorMap = computed(() => ({
  primary: 'primary',
  secondary: 'secondary',
  success: 'success',
  danger: 'danger',
  warning: 'warning',
}))

const getButtonStyle = () => {
  const colorMap = {
    primary: palette.primary,
    secondary: palette.secondary,
    success: palette.success,
    danger: palette.error,
    warning: palette.warning,
  }
  
  const color = colorMap[props.variant]
  
  return {
    backgroundColor: color,
    color: '#ffffff',
    padding: '0.75rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '600',
    borderRadius: '0.5rem',
    border: 'none',
    cursor: props.disabled ? 'not-allowed' : 'pointer',
    opacity: props.disabled ? '0.6' : '1',
    transition: 'all 0.2s ease-in-out',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    width: props.expand === 'block' ? '100%' : 'auto',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  }
}

const handleMouseEnter = (e) => {
  if (!props.disabled) {
    const colorMap = {
      primary: palette.primary,
      secondary: palette.secondary,
      success: palette.success,
      danger: palette.error,
      warning: palette.warning,
    }
    
    // Затемнение на 15% и добавляем тень
    const button = e.target.closest('button')
    if (button) {
      button.style.filter = 'brightness(0.85)'
      button.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.2)'
    }
  }
}

const handleMouseLeave = (e) => {
  if (!props.disabled) {
    const button = e.target.closest('button')
    if (button) {
      button.style.filter = 'brightness(1)'
      button.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)'
    }
  }
}
</script>
