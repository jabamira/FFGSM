<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">
      {{ label }}
      <span v-if="required" :style="{ color: palette.error }">*</span>
    </label>
    <input
      :id="id"
      :value="displayValue"
      :type="positiveIntegerOnly ? 'number' : (isDateType ? 'text' : type)"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :min="positiveIntegerOnly ? 0 : min"
      :max="positiveIntegerOnly ? 999999 : undefined"
      :step="positiveIntegerOnly ? 1 : step"
      :maxlength="isDateType ? 10 : undefined"
      :style="{ ...inputStyle, ...(isDateType ? { fontFamily: 'monospace' } : {}) }"
      class="w-full px-4 py-2 rounded-lg outline-none transition"
      @input="handleInput($event)"
      @keydown="handleKeyDown($event)"
      @blur="handleBlur($event)"
      @focus="$emit('focus')"
    />
    <p v-if="error" class="text-sm mt-1" :style="{ color: palette.error }">{{ error }}</p>
    <p v-if="hint && !error" class="text-sm mt-1" :style="{ color: palette.medium }">{{ hint }}</p>
  </div>
</template>

<script>
import { computed } from 'vue';
import { palette } from './theme';
import { formatDateToRussian, formatDateToISO } from '../../utils/dateUtils';

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
    uppercase: {
      type: Boolean,
      default: false,
    },
    disallowMinus: {
      type: Boolean,
      default: false,
    },
    positiveIntegerOnly: {
      type: Boolean,
      default: false,
    },
    min: {
      type: [String, Number],
      default: undefined,
    },
    step: {
      type: [String, Number],
      default: undefined,
    },
    id: {
      type: String,
      default: () => `input-${Math.random().toString(36).substr(2, 9)}`,
    },
  },
  emits: ['update:modelValue', 'blur', 'focus'],
  setup(props, { emit }) {
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

    const isDateType = computed(() => props.type === 'date');

    const displayValue = computed(() => {
      if (!props.modelValue) return '';
      
      // For date type, format ISO date to Russian format (DD.MM.YYYY)
      if (isDateType.value && props.modelValue && !props.modelValue.includes('.')) {
        return formatDateToRussian(props.modelValue);
      }
      
      return props.modelValue;
    });

    const handleInput = (event) => {
      let value = event.target.value;
      
      if (props.positiveIntegerOnly) {
        // Remove all non-digit characters
        value = value.replace(/[^\d]/g, '');
        // Limit to 6 digits (max 999999)
        value = value.slice(0, 6);
        event.target.value = value;
      } else if (props.disallowMinus && value.includes('-')) {
        // Remove minus signs if disallowMinus is true
        value = value.replace(/-/g, '');
        event.target.value = value;
      } else if (isDateType.value) {
        // For date input, allow only digits and dots, auto-format DD.MM.YYYY
        value = value.replace(/[^\d.]/g, '');
        
        // Auto-format as DD.MM.YYYY
        if (value.length >= 2 && !value.includes('.')) {
          value = value.slice(0, 2) + '.' + value.slice(2);
        }
        if (value.length >= 5 && value.split('.').length < 3) {
          const parts = value.split('.');
          if (parts[1]?.length >= 2) {
            value = parts[0] + '.' + parts[1].slice(0, 2) + '.' + parts[1].slice(2);
          }
        }
        
        event.target.value = value;
      }
      
      if (props.uppercase) {
        value = value.toUpperCase();
      }
      emit('update:modelValue', value);
    };

    const handleBlur = (event) => {
      let value = event.target.value;
      
      // If date is in Russian format (DD.MM.YYYY), convert to ISO for internal storage
      if (isDateType.value && value && value.includes('.')) {
        const isoDate = formatDateToISO(value);
        // Only emit if the conversion was successful (resulted in valid ISO format)
        if (isoDate && isoDate.match(/^\d{4}-\d{2}-\d{2}$/)) {
          emit('update:modelValue', isoDate);
        }
      }
      
      emit('blur');
    };

    const handleKeyDown = (event) => {
      if (props.positiveIntegerOnly) {
        // Block decimal point, minus, and other non-numeric keys
        if (event.key === '.' || event.key === ',' || event.key === '-' || event.code === 'Minus') {
          event.preventDefault();
        }
      } else if (props.disallowMinus && (event.key === '-' || event.code === 'Minus')) {
        // Block minus key if disallowMinus is true
        event.preventDefault();
      } else if (isDateType.value) {
        // Allow only digits, dots, backspace, delete, tab, arrows
        const allowedKeys = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End'];
        const isDigitOrDot = event.key === '.' || /^\d$/.test(event.key);
        
        if (!isDigitOrDot && !allowedKeys.includes(event.key)) {
          event.preventDefault();
        }
      }
    };

    return { palette, inputStyle, isDateType, displayValue, handleInput, handleBlur, handleKeyDown };
  },
};
</script>
