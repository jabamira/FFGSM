<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium" :style="{ color: palette.dark }">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>
    <div class="relative">
      <input
        ref="dateInput"
        type="text"
        class="w-full px-3 py-2 border rounded text-sm"
        :class="{ 
          'border-red-500 border-2': error,
          'cursor-pointer': !disabled,
          'cursor-not-allowed bg-gray-100': disabled
        }"
        :style="{ 
          borderColor: error ? '#ef4444' : palette.light, 
          color: disabled ? '#9ca3af' : palette.dark,
          backgroundColor: disabled ? '#f3f4f6' : 'white'
        }"
        readonly
        :placeholder="label"
        :disabled="disabled"
      />
      <div 
        class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none"
        :style="{ color: palette.medium }"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    </div>
    <div v-if="formattedDate" class="text-xs mt-1" :style="{ color: palette.medium }">
      Выбранная дата: {{ formattedDate }}
    </div>
    <div v-if="error" class="text-xs text-red-500 mt-1">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { palette } from './theme';
import { onMounted, ref, computed } from 'vue';
import flatpickr from 'flatpickr';
import { Russian } from 'flatpickr/dist/l10n/ru';
import 'flatpickr/dist/flatpickr.min.css';

const dateInput = ref(null);
let picker = null;

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Дата'
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue']);

const formattedDate = computed(() => {
  if (!props.modelValue) return '';
  const date = new Date(props.modelValue + 'T00:00:00');
  return new Intl.DateTimeFormat('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
});

onMounted(() => {
  // Helper function to get today's date in Y-m-d format
  const getTodayString = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Helper function to parse Y-m-d string to Date object
  const parseApiDate = (dateString) => {
    if (!dateString) return null;
    const [year, month, day] = dateString.split('-');
    return new Date(year, parseInt(month) - 1, day);
  };

  // Helper function to format date to standard Y-m-d format for API
  const toApiFormat = (date) => {
    if (!date) return '';
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const todayString = getTodayString();
  const defaultDate = props.modelValue ? parseApiDate(props.modelValue) : parseApiDate(todayString);

  // Date picker
  picker = flatpickr(dateInput.value, {
    mode: 'single',
    dateFormat: 'd.m.Y', // Russian format for display
    locale: Russian,
    defaultDate: defaultDate, // Set today's date by default
    onChange: (selectedDates) => {
      const newDate = selectedDates[0] ? toApiFormat(selectedDates[0]) : '';
      emit('update:modelValue', newDate);
    },
    disableMobile: false,
    disable: [props.disabled ? () => true : () => false],  // Disable all dates if disabled prop is true
  });

  // Initialize with today's date if no value provided
  if (!props.modelValue) {
    emit('update:modelValue', todayString);
  }
});
</script>

<style scoped>
/* Customize flatpickr styling to match palette */
:deep(.flatpickr-calendar) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-family: inherit;
}

:deep(.flatpickr-current-month) {
  padding: 12px;
}

:deep(.flatpickr-prev-month, .flatpickr-next-month) {
  height: 32px;
}

:deep(.prevMonthDay, .nextMonthDay) {
  color: #ccc;
}

:deep(.flatpickr-day.selected) {
  background-color: var(--primary, #3b82f6);
  border-color: var(--primary, #3b82f6);
}

:deep(.flatpickr-day:hover) {
  background-color: #e8f0fe;
}

:deep(.flatpickr-day.today) {
  border-color: #3b82f6;
}

:deep(.flatpickr-day.today:hover) {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}
</style>
