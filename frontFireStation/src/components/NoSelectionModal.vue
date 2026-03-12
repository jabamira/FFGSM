<template>
  <Modal
    :is-open="isOpen"
    title="Внимание"
    @close="closeModal"
  >
    <div class="space-y-4 min-w-96">
      <div class="flex flex-col items-center">
        <div class="flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 mb-4">
          <svg class="h-8 w-8 text-yellow-600" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"></path>
          </svg>
        </div>
        <p :style="{ color: palette.dark }" class="font-semibold text-center">Не выбраны элементы</p>
        <p class="text-gray-600 text-sm mt-3 text-center">
          Пожалуйста, выберите хотя бы один элемент из списка для выполнения этого действия.
        </p>
      </div>
    </div>
    <template #footer>
      <Button variant="primary" size="md" @click="closeModal">Понятно</Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref } from 'vue';
import { Modal, Button, palette } from './ui/importUi';

const isOpen = ref(false);

const openModal = () => {
  isOpen.value = true;
};

const closeModal = () => {
  isOpen.value = false;
};

defineExpose({
  openModal,
  closeModal
});
</script>
