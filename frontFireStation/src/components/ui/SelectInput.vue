<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">
      {{ label }}
      <span v-if="required" :style="{ color: palette.error }">*</span>
    </label>
    <select
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :style="selectStyle"
      class="w-full px-4 py-2 rounded-lg outline-none transition"
      @change="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <p v-if="error" class="text-sm mt-1" :style="{ color: palette.error }">{{ error }}</p>
    <p v-if="hint && !error" class="text-sm mt-1" :style="{ color: palette.medium }">{{ hint }}</p>
  </div>
</template>

<script>
import { computed } from 'vue';
import { palette } from './theme';

export default {
  name: 'SelectInput',
  props: {
    modelValue: {
      type: [String, Number],
      default: '',
    },
    options: {
      type: Array,
      required: true,
      // Expected format: [{ value: 'val1', label: 'Label 1' }, ...]
    },
    label: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: 'Select an option',
    },
    error: {
      type: String,
      default: '',
    },
    hint: {
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
    id: {
      type: String,
      default: () => `select-${Math.random().toString(36).substr(2, 9)}`,
    },
  },
  emits: ['update:modelValue', 'blur', 'focus'],
  setup(props) {
    const selectStyle = computed(() => {
      return {
        color: palette.dark,
        borderColor: props.error ? palette.error : palette.light,
        boxShadow: props.error 
          ? `0 0 0 3px ${palette.error}20` 
          : `0 0 0 0 transparent`,
        backgroundColor: props.disabled ? `${palette.light}20` : 'white',
        border: `1px solid ${props.error ? palette.error : palette.light}`,
        '--tw-ring-color': props.error ? palette.error : palette.primary,
      };
    });

    return { palette, selectStyle };
  },
};
</script>
