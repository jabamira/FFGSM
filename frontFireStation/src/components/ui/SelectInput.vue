<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-medium mb-2" :style="{ color: palette.dark }">
      {{ label }}
      <span v-if="required" :style="{ color: palette.error }">*</span>
    </label>
    
    <div class="relative">
      <!-- Input с поиском -->
      <input
        :id="id"
        :value="isOpen ? searchQuery : selectedLabel"
        type="text"
        :placeholder="placeholder || 'Поиск или выбор...'"
        :disabled="disabled"
        :style="inputStyle"
        class="w-full px-4 py-2 rounded-lg outline-none transition"
        @input="onSearchInput"
        @focus="openDropdown"
        @blur="closeDropdownDelay"
      />
      
      <!-- Иконка стрелки -->
      <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" :style="{ color: palette.medium }">
        <svg v-if="!isOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7 7 7m0 0v12m0-12l-7 7m0 0l-7-7"></path>
        </svg>
      </div>
      
      <!-- Выпадающий список опций -->
      <div
        v-if="isOpen"
        class="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto"
        :style="{ borderColor: palette.light, border: `1px solid ${palette.light}` }"
      >
        <div v-if="filteredOptions.length === 0" class="px-4 py-2 text-sm" :style="{ color: palette.medium }">
          Нет результатов
        </div>
        
        <div
          v-for="option in filteredOptions"
          :key="option.value"
          class="px-4 py-2 cursor-pointer hover:bg-blue-50 transition"
          :style="{ 
            backgroundColor: selectedValue === option.value ? `${palette.primary}20` : 'transparent',
            color: palette.dark
          }"
          @click="selectOption(option)"
        >
          {{ option.label }}
        </div>
      </div>
    </div>
    
    <p v-if="error" class="text-sm mt-1" :style="{ color: palette.error }">{{ error }}</p>
    <p v-if="hint && !error" class="text-sm mt-1" :style="{ color: palette.medium }">{{ hint }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { palette } from './theme';

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  options: {
    type: Array,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Поиск или выбор...',
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
});

const emit = defineEmits(['update:modelValue', 'blur', 'focus']);

const isOpen = ref(false);
const searchQuery = ref('');
let closeTimeout;

const selectedValue = computed(() => props.modelValue);

const selectedLabel = computed(() => {
  const option = props.options.find(o => o.value === props.modelValue);
  return option?.label || '';
});

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options;
  
  const query = searchQuery.value.toLowerCase();
  return props.options.filter(option =>
    option.label.toLowerCase().includes(query)
  );
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
    '--tw-ring-color': props.error ? palette.error : palette.primary,
  };
});

const openDropdown = () => {
  if (props.disabled) return;
  isOpen.value = true;
  searchQuery.value = '';
  emit('focus');
};

const closeDropdownDelay = () => {
  closeTimeout = setTimeout(() => {
    isOpen.value = false;
    searchQuery.value = '';
  }, 150);
};

const selectOption = (option) => {
  emit('update:modelValue', option.value);
  isOpen.value = false;
  searchQuery.value = '';
  clearTimeout(closeTimeout);
};

const onSearchInput = (event) => {
  searchQuery.value = event.target.value;
  // Открываем список при вводе, если он закрыт
  if (!isOpen.value) {
    isOpen.value = true;
  }
  // Очищаем таймаут закрытия при вводе
  clearTimeout(closeTimeout);
};
</script>
