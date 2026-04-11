<template>
  <div class="mb-4">
    <ion-label v-if="label" class="text-sm font-medium block mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </ion-label>
    <ion-item class="rounded-lg border" :style="{ borderColor: palette.light }">
      <ion-input
        :value="modelValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        @ion-input="$emit('update:modelValue', $event.target.value)"
        @focus="$emit('focus')"
        @blur="handleBlur"
      />
    </ion-item>
    <p v-if="error" class="text-sm mt-2 text-red-500">{{ error }}</p>
    <p v-if="hint && !error" class="text-sm mt-2" :style="{ color: palette.medium }">
      {{ hint }}
    </p>
  </div>
</template>

<script setup>
import { IonItem, IonInput, IonLabel } from '@ionic/vue'
import { palette } from './theme'

defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  type: {
    type: String,
    default: 'text',
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur'])

const handleBlur = () => {
  emit('blur')
}
</script>
