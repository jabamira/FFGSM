<template>
  <Modal
    ref="modalRef"
    :is-open="isOpen"
    title="Ошибка"
    @close="closeModal"
  >
    <div class="space-y-4 min-w-96">
      <div class="rounded-lg p-4" :style="{ backgroundColor: `${palette.error}15`, borderLeft: `4px solid ${palette.error}` }">
        <p class="font-semibold" :style="{ color: palette.error }">{{ errorTitle }}</p>
        <p class="text-sm mt-2" :style="{ color: palette.dark }">{{ errorMessage }}</p>
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
import { ref } from 'vue';
import { Modal, Button, palette } from './ui/importUi';
import { formatFieldName } from '../utils/errorUtils';

const modalRef = ref(null);

const isOpen = ref(false);
const errorTitle = ref('');
const errorMessage = ref('');
const fieldErrors = ref([]);

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
    errorMessage.value = data.detail || data.message || 'Проверьте заполненные данные';
    
    // Парсим field errors
    fieldErrors.value = [];
    if (typeof data === 'object') {
      Object.entries(data).forEach(([field, messages]) => {
        if (field !== 'detail' && field !== 'message' && messages) {
          const messageText = Array.isArray(messages) 
            ? messages.join(', ') 
            : String(messages);
          fieldErrors.value.push({
            field: formatFieldName(field),
            message: messageText
          });
        }
      });
    }
  } else {
    errorTitle.value = 'Произошла ошибка';
    errorMessage.value = error.message || 'Неизвестная ошибка';
    fieldErrors.value = [];
  }
  
  isOpen.value = true;
};

const closeModal = () => {
  isOpen.value = false;
  if (modalRef.value) {
    modalRef.value.isErrorModal.value = false;
  }
  errorTitle.value = '';
  errorMessage.value = '';
  fieldErrors.value = [];
};

defineExpose({
  openModal,
  closeModal
});
</script>
