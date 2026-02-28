<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">
      {{ label }}
      <span v-if="required" :style="{ color: palette.error }">*</span>
    </label>
    <input
      :id="id"
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :style="inputStyle"
      class="w-full px-4 py-2 rounded-lg outline-none transition"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    />
    <p v-if="error" class="text-sm mt-1" :style="{ color: palette.error }">{{ error }}</p>
    <p v-if="hint && !error" class="text-sm mt-1" :style="{ color: palette.medium }">{{ hint }}</p>
  </div>
</template>

<script>
import { computed } from 'vue';
import { palette } from './theme';

export default {
  name: 'TextInput',
  props: {
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
      default: () => `input-${Math.random().toString(36).substr(2, 9)}`,
    },
  },
  emits: ['update:modelValue', 'blur', 'focus'],
  setup(props) {
    const inputStyle = computed(() => {
      const style = {
        color: palette.dark,
        borderColor: props.error ? palette.error : palette.light,
        boxShadow: props.error 
          ? `0 0 0 3px ${palette.error}20` 
          : `0 0 0 0 transparent`,
        backgroundColor: props.disabled ? `${palette.light}20` : 'white',
        border: `1px solid ${props.error ? palette.error : palette.light}`,
      };

      // Focus ring color
      return {
        ...style,
        '--tw-ring-color': props.error ? palette.error : palette.primary,
      };
    });

    return { palette, inputStyle };
  },
};
</script>
