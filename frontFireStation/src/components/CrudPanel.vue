<template>
  <div v-if="showPanel" 
    class="fixed z-40 bg-white rounded-lg shadow-lg border"
    :style="{
      borderColor: palette.light,
      left: `${position.x}px`,
      top: `${position.y}px`,
      cursor: isPinned ? 'default' : 'grab',
    }"
    @mousedown="startDrag"
  >
    <div class="p-4 pr-14 flex items-center gap-3 relative">
      <!-- Кнопки CRUD -->
      <Button 
        v-if="auth.crudPermissions.canCreate"
        @click="$emit('create')" 
        :label="createLabel"
        variant="primary"
        size="sm"
        :disabled="isCreateDisabled"
      />
      <Button 
        v-if="auth.crudPermissions.canDelete"
        @click="$emit('delete')" 
        :label="deleteLabel"
        variant="danger"
        size="sm"
        :disabled="isDeleteDisabled"
      />

      <!-- Pin button в правом углу -->
      <button
        @click.stop="togglePin"
        :title="isPinned ? 'Открепить' : 'Закрепить'"
        class="absolute top-1 right-1 p-1.5 rounded-full hover:shadow-md transition"
      >
        <img 
          :src="pinIcon"
          alt="pin"
          class="w-5 h-5"
          :style="{ 
            opacity: isPinned ? 1 : 0.6, 
            filter: `${isPinned ? '' : 'grayscale(100%)'} brightness(0) saturate(100%) invert(28%) sepia(77%) saturate(1200%) hue-rotate(200deg)`,
          }"
        />
      </button>
    </div>
  </div>
</template>

<script setup>
import { Button, palette } from './ui/importUi';
import { useAuthStore } from '../stores/auth';
import { computed, ref } from 'vue';
import pinIcon from '../img/free-icon-pin-3297677.png';

const auth = useAuthStore();

defineProps({
  createLabel: {
    type: String,
    default: 'Создать'
  },
  deleteLabel: {
    type: String,
    default: 'Удалить'
  },
  isDeleteDisabled: {
    type: Boolean,
    default: false
  },
  isCreateDisabled: {
    type: Boolean,
    default: false
  }
});

defineEmits(['create', 'delete']);

// Состояние панели
const position = ref({ x: window.innerWidth / 2 - 100, y: window.innerHeight - 120 });
const isPinned = ref(false);
const isDragging = ref(false);
const dragOffset = ref({ x: 0, y: 0 });

// Показываем панель только если хотя бы одно разрешение true
const showPanel = computed(() => {
  return (
    auth.crudPermissions.canCreate ||
    auth.crudPermissions.canDelete
  );
});

/**
 * Начать перетаскивание
 */
const startDrag = (event) => {
  if (isPinned.value) return;
  
  // Не начинаем drag если зажали на кнопке
  if (event.target.closest('button[title]')) return;

  isDragging.value = true;
  dragOffset.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y,
  };

  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);
};

/**
 * Перемещение панели
 */
const onDrag = (event) => {
  if (!isDragging.value || isPinned.value) return;

  position.value = {
    x: event.clientX - dragOffset.value.x,
    y: event.clientY - dragOffset.value.y,
  };
};

/**
 * Завершить перетаскивание
 */
const stopDrag = () => {
  isDragging.value = false;
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
};

/**
 * Переключить закрепление панели
 */
const togglePin = () => {
  isPinned.value = !isPinned.value;
};
</script>
