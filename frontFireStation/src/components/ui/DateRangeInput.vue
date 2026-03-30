<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium" :style="{ color: palette.dark }">
      {{ label }}
    </label>
    <div class="flex flex-col lg:flex-row gap-3 items-stretch lg:items-end">
      <!-- Start Date Picker -->
      <div class="flex-1">
        <div class="relative">
          <input
            ref="startDateInput"
            type="text"
            class="w-full px-3 py-2 border rounded text-sm cursor-pointer"
            :style="{ 
              borderColor: palette.light, 
              color: palette.dark,
              backgroundColor: 'white'
            }"
            readonly
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
        <div class="text-xs mt-1" :style="{ color: palette.medium }">{{ startLabel }}</div>
      </div>

      <!-- Separator -->
      <div class="flex items-center justify-center text-sm hidden lg:flex" :style="{ color: palette.medium }">→</div>
      <div class="text-center lg:hidden text-xs" :style="{ color: palette.medium }">по</div>

      <!-- End Date Picker -->
      <div class="flex-1">
        <div class="relative">
          <input
            ref="endDateInput"
            type="text"
            class="w-full px-3 py-2 border rounded text-sm cursor-pointer"
            :style="{ 
              borderColor: palette.light, 
              color: palette.dark,
              backgroundColor: 'white'
            }"
            readonly
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
        <div class="text-xs mt-1" :style="{ color: palette.medium }">{{ endLabel }}</div>
      </div>

      <!-- Clear Button -->
      <Button
        v-if="showClear && (modelValue.start || modelValue.end)"
        @click="clearDates"
        label="Очистить"
        :style="{ minWidth: '120px' }"
        variant="secondary"
      />
    </div>
  </div>
</template>

<script setup>
import { palette } from './theme';
import Button from './Button.vue';
import { onMounted, ref } from 'vue';
import flatpickr from 'flatpickr';
import { Russian } from 'flatpickr/dist/l10n/ru';
import 'flatpickr/dist/flatpickr.min.css';

const startDateInput = ref(null);
const endDateInput = ref(null);
let startPicker = null;
let endPicker = null;

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    validator: (obj) => {
      return 'start' in obj && 'end' in obj;
    }
  },
  label: {
    type: String,
    default: 'Период'
  },
  startLabel: {
    type: String,
    default: 'Начало'
  },
  endLabel: {
    type: String,
    default: 'Конец'
  },
  showClear: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:modelValue']);

const clearDates = () => {
  emit('update:modelValue', { start: '', end: '' });
  if (startPicker) {
    startPicker.setDate(null);
  }
  if (endPicker) {
    endPicker.setDate(null);
  }
};

onMounted(() => {
  // Helper function to format date to standard Y-m-d format for API
  const toApiFormat = (date) => {
    if (!date) return '';
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Start date picker
  startPicker = flatpickr(startDateInput.value, {
    mode: 'single',
    dateFormat: 'd.m.Y', // Russian format for display
    locale: Russian,
    defaultDate: props.modelValue.start || null,
    onChange: (selectedDates) => {
      const newStart = selectedDates[0] ? toApiFormat(selectedDates[0]) : '';
      emit('update:modelValue', { 
        start: newStart, 
        end: props.modelValue.end 
      });
    },
    disableMobile: false,
  });

  // End date picker
  endPicker = flatpickr(endDateInput.value, {
    mode: 'single',
    dateFormat: 'd.m.Y', // Russian format for display
    locale: Russian,
    defaultDate: props.modelValue.end || null,
    onChange: (selectedDates) => {
      const newEnd = selectedDates[0] ? toApiFormat(selectedDates[0]) : '';
      emit('update:modelValue', { 
        start: props.modelValue.start,
        end: newEnd
      });
    },
    disableMobile: false,
  });
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
</style>
