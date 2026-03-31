<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">
      {{ label }}
      <span v-if="required" :style="{ color: palette.error }">*</span>
    </label>
    <div class="relative">
      <input
        :id="id"
        ref="timeInputRef"
        :value="displayValue"
        type="text"
        :placeholder="placeholder"
        :disabled="disabled"
        :style="inputStyle"
        class="w-full px-4 py-2 rounded-lg outline-none transition cursor-pointer"
        @input="handleManualInput"
        maxlength="5"
      />
      <svg 
        class="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none"
        :style="{ color: palette.dark }"
        width="20" 
        height="20" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        stroke-width="2"
      >
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
    </div>
    <p v-if="error" class="text-sm mt-1" :style="{ color: palette.error }">{{ error }}</p>
    <p v-if="hint && !error" class="text-sm mt-1" :style="{ color: palette.medium }">{{ hint }}</p>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import flatpickr from 'flatpickr';
import { Russian } from 'flatpickr/dist/l10n/ru.js';
import 'flatpickr/dist/flatpickr.min.css';
import { palette } from './theme';

export default {
  name: 'TimeInput',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: 'ЧЧ:МММ',
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
      default: () => `time-input-${Math.random().toString(36).substr(2, 9)}`,
    },
  },
  emits: ['update:modelValue', 'blur', 'focus'],
  setup(props, { emit }) {
    const timeInputRef = ref(null);
    let flatpickrInstance = null;

    const displayValue = ref(props.modelValue);

    watch(() => props.modelValue, (newVal) => {
      displayValue.value = newVal;
    });

    const inputStyle = computed(() => {
      return {
        color: palette.dark,
        borderColor: props.error ? palette.error : palette.light,
        boxShadow: props.error 
          ? `0 0 0 3px ${palette.error}20` 
          : `0 0 0 0 transparent`,
        backgroundColor: props.disabled ? `${palette.light}20` : 'white',
        border: `1px solid ${props.error ? palette.error : palette.light}`,
      };
    });

    // Получить текущее время в формате HH:MM
    const getCurrentTime = () => {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      return `${hours}:${minutes}`;
    };

    // Форматировать время с маской HH:MM
    const formatTimeInput = (input) => {
      // Оставить только цифры
      const digits = input.replace(/\D/g, '');
      
      // Если длина меньше или равна 2, просто возвращаем цифры
      if (digits.length <= 2) {
        return digits;
      }
      
      // Если больше 2, добавляем двоеточие
      if (digits.length >= 3) {
        return `${digits.slice(0, 2)}:${digits.slice(2, 4)}`;
      }
      
      return digits;
    };

    const handleManualInput = (event) => {
      const input = event.target.value;
      const formatted = formatTimeInput(input);
      
      displayValue.value = formatted;
      emit('update:modelValue', formatted);
      
      // Обновить значение поля
      event.target.value = formatted;
    };

    onMounted(() => {
      if (timeInputRef.value && !props.disabled) {
        // Инициализировать текущим временем если пусто
        const initialTime = props.modelValue || getCurrentTime();
        displayValue.value = initialTime;
        
        flatpickrInstance = flatpickr(timeInputRef.value, {
          enableTime: true,
          noCalendar: true,
          hourIncrement: 1,
          minuteIncrement: 1,
          time_24hr: true,
          dateFormat: 'H:i',
          locale: Russian,
          position: 'auto',
          onClose: (selectedDates, dateStr) => {
            displayValue.value = dateStr;
            emit('update:modelValue', dateStr);
          },
          onChange: (selectedDates, dateStr) => {
            displayValue.value = dateStr;
          },
          defaultDate: initialTime || undefined,
        });
      }
    });

    return {
      palette,
      timeInputRef,
      displayValue,
      inputStyle,
      handleManualInput,
    };
  },
};
</script>

<style scoped>
/* Customize flatpickr styles */
:deep(.flatpickr-calendar) {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.15);
  border-radius: 0.5rem;
  width: 320px !important;
  z-index: 9999 !important;
}

:deep(.flatpickr-time) {
  padding: 12px 8px;
  border-top: 1px solid #e5e7eb;
  height: auto;
}

:deep(.flatpickr-time input) {
  font-size: 18px;
  height: 50px;
  padding: 8px 4px;
  font-weight: 600;
}

:deep(.flatpickr-time span.flatpickr-am-pm) {
  align-self: center;
  font-size: 16px;
  padding: 0 8px;
}

:deep(.numInputWrapper) {
  flex: 1;
  min-width: 60px;
}

:deep(.numInputWrapper input) {
  font-size: 18px;
  text-align: center;
  font-weight: 600;
  height: 50px;
  padding: 8px;
}

:deep(.numInputWrapper .arrowUp)::after {
  border-bottom-color: #666;
}

:deep(.numInputWrapper .arrowDown)::after {
  border-top-color: #666;
}

:deep(.flatpickr-time .numInputWrapper span.arrowUp),
:deep(.flatpickr-time .numInputWrapper span.arrowDown) {
  width: 30px;
  height: 20px;
}

:deep(.flatpickr-time .numInputWrapper span.arrowUp)::after {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid #666;
}

:deep(.flatpickr-time .numInputWrapper span.arrowDown)::after {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid #666;
}
</style>
