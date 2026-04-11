<template>
  <ion-alert
    :is-open="isOpen"
    :header="title"
    :message="message"
    :buttons="buttons"
    @didDismiss="didDismiss"
  />
</template>

<script setup>
import { reactive, computed } from 'vue'
import { IonAlert } from '@ionic/vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: 'Alert',
  },
  message: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    enum: ['success', 'error', 'warning', 'info'],
    default: 'info',
  },
  actions: {
    type: Array,
    default: () => [
      {
        text: 'OK',
        handler: () => {},
      },
    ],
  },
})

const emit = defineEmits(['close'])

const buttons = computed(() =>
  props.actions.map(action => ({
    text: action.text,
    handler: () => {
      action.handler()
      emit('close')
    },
  }))
)

const didDismiss = () => {
  emit('close')
}
</script>
