<template>
  <Modal
    ref="modalRef"
    :is-open="currentIsOpen"
    :title="currentTitle"
    @close="closeModal"
  >
    <div class="space-y-4 min-w-96">
      <div class="rounded-lg p-4" :style="{ backgroundColor: `${palette.error}15`, borderLeft: `4px solid ${palette.error}` }">
        <p class="font-semibold" :style="{ color: palette.error }">{{ currentTitle }}</p>
        <p class="text-sm mt-2" :style="{ color: palette.dark }">{{ currentMessage }}</p>
      </div>

      <!-- Детали ошибок (если есть fieldErrors) -->
      <div v-if="fieldErrors.length > 0" class="space-y-2">
        <p class="text-sm font-semibold" :style="{ color: palette.dark }">Ошибки в полях:</p>
        <div 
          v-for="(error, index) in fieldErrors" 
          :key="index"
          :style="{ 
            padding: '8px 12px',
            borderRadius: '6px',
            backgroundColor: `${palette.error}10`,
            borderLeft: `3px solid ${palette.error}`
          }"
        >
          <p class="text-sm" :style="{ color: palette.dark }">
            <span class="font-medium" :style="{ color: palette.error }">{{ error.field }}:</span> {{ error.message }}
          </p>
        </div>
      </div>
    </div>

    <template #footer>
      <Button variant="primary" size="md" @click="closeModal">Закрыть</Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Modal, Button, palette } from './ui/importUi';
import { formatFieldName } from '../utils/errorUtils';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['close']);

const modalRef = ref(null);

const internalIsOpen = ref(false);
const errorTitle = ref('');
const errorMessage = ref('');
const fieldErrors = ref([]);

// Determine if using prop-based or method-based API
const currentIsOpen = computed(() => {
  return props.isOpen !== false ? props.isOpen : internalIsOpen.value;
});

const currentTitle = computed(() => {
  return props.title || errorTitle.value || 'Ошибка';
});

const currentMessage = computed(() => {
  return props.message || errorMessage.value;
});

const closeModal = () => {
  internalIsOpen.value = false;
  emit('close');
  errorTitle.value = '';
  errorMessage.value = '';
  fieldErrors.value = [];
};

const openModal = (error) => {
  if (modalRef.value) {
    modalRef.value.isErrorModal = true;
  }
  // Парсим ошибку от сервера
  if (typeof error === 'string') {
    errorTitle.value = 'Ошибка операции';
    errorMessage.value = error;
    fieldErrors.value = [];
  } else if (error.response?.data) {
    const data = error.response.data;
    errorTitle.value = 'Ошибка при сохранении';
    
    // Обработка ValidationError (список строк)
    if (Array.isArray(data)) {
      errorMessage.value = data.length > 0 ? data[0] : 'Ошибка при сохранении данных';
      fieldErrors.value = [];
    } 
    // Обработка объекта ошибок
    else if (typeof data === 'object') {
      // Ищем основное сообщение об ошибке
      errorMessage.value = data.detail || data.message || data.non_field_errors?.[0] || 'Проверьте заполненные данные';
      
      // Парсим field errors
      fieldErrors.value = [];
      Object.entries(data).forEach(([field, messages]) => {
        if (field !== 'detail' && field !== 'message' && field !== 'non_field_errors' && messages) {
          const messageText = Array.isArray(messages) 
            ? messages.join(', ') 
            : String(messages);
          fieldErrors.value.push({
            field: formatFieldName(field),
            message: messageText
          });
        }
      });
    } else {
      errorMessage.value = 'Проверьте заполненные данные';
      fieldErrors.value = [];
    }
  } else {
    errorTitle.value = 'Произошла ошибка';
    errorMessage.value = error.message || 'Неизвестная ошибка';
    fieldErrors.value = [];
  }
  
  internalIsOpen.value = true;
};

defineExpose({
  openModal,
  closeModal
});
</script>
