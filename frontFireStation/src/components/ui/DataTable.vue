<template>
  <div class="overflow-x-auto rounded-lg border" :style="{ borderColor: palette.light }">
    <table class="w-full border-collapse">
      <!-- Table Header -->
      <thead>
        <tr :style="{ backgroundColor: `${palette.primary}15`, borderColor: palette.light, borderBottomWidth: '1px' }">
          <th class="w-12 px-4 py-3 text-left">
            <input
              v-if="selectable && showSelectAll"
              type="checkbox"
              :checked="allSelected"
              @change="toggleSelectAll"
              class="w-4 h-4 cursor-pointer"
            />
          </th>
          <th
            v-for="column in columns"
            :key="column.key"
            class="px-4 py-3 text-sm cursor-pointer font-semibold"
            :style="{ color: palette.dark }"
            @click="sortBy(column.key)"
          >
            <div class="flex items-center gap-2 hover:opacity-70">
              {{ column.label }}
              <span v-if="sortKey === column.key" class="text-xs">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </div>
          </th>
          <th v-if="actions" class="px-4 py-3 text-sm font-semibold" :style="{ color: palette.dark }">Actions</th>
        </tr>
      </thead>

      <!-- Table Body -->
      <tbody>
        <tr
          v-for="(row, idx) in paginatedData"
          :key="idx"
          class="border-b hover:opacity-75 cursor-pointer"
          :style="{ borderColor: palette.light, backgroundColor: idx % 2 === 0 ? 'white' : `${palette.light}10` }"
          @click="$emit('row-click', row, idx)"
        >
          <td class="w-12 px-4 py-3">
            <input
              v-if="selectable"
              type="checkbox"
              :checked="selectedRows.includes(getRowId(row))"
              @mousedown.stop.prevent="onCheckboxMouseDown(idx)"
              @mouseover="onCheckboxMouseOver(idx)"
              @click.stop.prevent
              class="w-4 h-4 cursor-pointer"
            />
          </td>
          <td
            v-for="column in columns"
            :key="column.key"
            class="px-4 py-3 text-sm"
            :style="{ color: palette.dark }"
          >
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ formatValue(row[column.key], column) }}
            </slot>
          </td>
          <td v-if="actions" class="px-4 py-3 text-sm">
            <div class="flex gap-2">
              <slot name="actions" :row="row" :index="idx">
                <button
                  v-for="action in actions"
                  :key="action.name"
                  @click="$emit(action.event, row, idx)"
                  :style="{ color: action.color || palette.primary }"
                  class="text-sm font-medium hover:opacity-70"
                >
                  {{ action.label }}
                </button>
              </slot>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Empty State -->
    <div v-if="data.length === 0" class="text-center py-8" :style="{ color: palette.medium }">
      <p>Данные отсутствуют</p>
    </div>

    <!-- Pagination -->
    <div
      v-if="paginate && totalPages > 1"
      class="flex items-center justify-between px-4 py-4 border-t"
      :style="{ borderColor: palette.light, backgroundColor: `${palette.light}10` }"
    >
      <div class="text-sm" :style="{ color: palette.medium }">
        Page {{ currentPage }} of {{ totalPages }} ({{ data.length }} total)
      </div>
      <div class="flex gap-2">
        <button
          @click="prevPage"
          :disabled="currentPage === 1"
          class="px-3 py-1 rounded transition disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-70"
          :style="{ borderColor: palette.light, border: `1px solid ${palette.light}`, color: palette.dark }"
        >
          ← Prev
        </button>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="px-3 py-1 rounded transition disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-70"
          :style="{ borderColor: palette.light, border: `1px solid ${palette.light}`, color: palette.dark }"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue';
import { palette } from './theme';

export default {
  name: 'DataTable',
  props: {
    data: {
      type: Array,
      required: true,
    },
    columns: {
      type: Array,
      required: true,
      // Expected format: [{ key: 'id', label: 'ID', type: 'string' }, ...]
    },
    actions: {
      type: Array,
      default: null,
      // Expected format: [{ name: 'edit', label: 'Edit', event: 'edit-row', color: '...' }, ...]
    },
    selectable: {
      type: Boolean,
      default: false,
    },
    showSelectAll: {
      type: Boolean,
      default: true,
    },
    paginate: {
      type: Boolean,
      default: true,
    },
    pageSize: {
      type: Number,
      default: 10,
    },
    rowIdKey: {
      type: String,
      default: 'id',
    },
  },
  emits: ['row-selected', 'row-click', 'sort', 'edit-row', 'delete-row', 'view-row'],
  setup(props, { emit }) {
    const currentPage = ref(1);
    const sortKey = ref(null);
    const sortOrder = ref('asc');
    const selectedRows = ref([]);
    const isDragging = ref(false);
    const dragStartIdx = ref(null);
    const dragMode = ref(null); // 'select' или 'unselect'
    const selectedRowsBeforeDrag = ref([]); // Состояние до начала drag

    const sortedData = computed(() => {
      if (!sortKey.value) return [...props.data];

      return [...props.data].sort((a, b) => {
        const aVal = a[sortKey.value];
        const bVal = b[sortKey.value];

        if (typeof aVal === 'string') {
          return sortOrder.value === 'asc'
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
        }

        return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal;
      });
    });

    const paginatedData = computed(() => {
      if (!props.paginate) return sortedData.value;

      const start = (currentPage.value - 1) * props.pageSize;
      const end = start + props.pageSize;
      return sortedData.value.slice(start, end);
    });

    const totalPages = computed(() =>
      Math.ceil(props.data.length / props.pageSize)
    );

    const allSelected = computed(() =>
      selectedRows.value.length === paginatedData.value.length &&
      paginatedData.value.length > 0
    );

    const getRowId = (row) => {
      return row[props.rowIdKey];
    };

    const getRowIndex = (rowId) => {
      return paginatedData.value.findIndex(row => getRowId(row) === rowId);
    };

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortKey.value = key;
        sortOrder.value = 'asc';
      }
      emit('sort', { key, order: sortOrder.value });
    };

    const toggleRow = (idx) => {
      const rowId = getRowId(paginatedData.value[idx]);
      const index = selectedRows.value.indexOf(rowId);
      if (index > -1) {
        selectedRows.value.splice(index, 1);
      } else {
        selectedRows.value.push(rowId);
      }
      emit('row-selected', selectedRows.value);
    };

    const toggleSelectAll = () => {
      if (allSelected.value) {
        selectedRows.value = [];
      } else {
        selectedRows.value = paginatedData.value.map(row => getRowId(row));
      }
      emit('row-selected', selectedRows.value);
    };

    const prevPage = () => {
      if (currentPage.value > 1) currentPage.value--;
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) currentPage.value++;
    };

    const formatValue = (value, column) => {
      if (column.type === 'date') {
        return new Date(value).toLocaleDateString();
      }
      if (column.type === 'currency') {
        return `$${parseFloat(value).toFixed(2)}`;
      }
      if (column.type === 'percent') {
        return `${parseFloat(value).toFixed(2)}%`;
      }
      return value || '-';
    };

    const onCheckboxMouseDown = (idx) => {
      // Получаем ID строки
      const rowId = getRowId(paginatedData.value[idx]);
      const isSelected = selectedRows.value.includes(rowId);
      dragMode.value = isSelected ? 'unselect' : 'select';
      
      // Сохраняем состояние ДО начала drag
      selectedRowsBeforeDrag.value = [...selectedRows.value];
      
      isDragging.value = true;
      dragStartIdx.value = idx;
      
      // Применяем режим к стартовой строке
      if (dragMode.value === 'select') {
        if (!selectedRows.value.includes(rowId)) {
          selectedRows.value.push(rowId);
        }
      } else {
        const index = selectedRows.value.indexOf(rowId);
        if (index > -1) {
          selectedRows.value.splice(index, 1);
        }
      }
    };

    const onCheckboxMouseOver = (idx) => {
      if (!isDragging.value || dragStartIdx.value === null || !dragMode.value) return;

      // Восстанавливаем состояние ДО drag
      selectedRows.value = [...selectedRowsBeforeDrag.value];

      const start = Math.min(dragStartIdx.value, idx);
      const end = Math.max(dragStartIdx.value, idx);

      if (dragMode.value === 'select') {
        // Выбираем все строки от start до end
        for (let i = start; i <= end; i++) {
          const rowId = getRowId(paginatedData.value[i]);
          if (!selectedRows.value.includes(rowId)) {
            selectedRows.value.push(rowId);
          }
        }
      } else {
        // Удаляем все строки от start до end
        for (let i = start; i <= end; i++) {
          const rowId = getRowId(paginatedData.value[i]);
          const index = selectedRows.value.indexOf(rowId);
          if (index > -1) {
            selectedRows.value.splice(index, 1);
          }
        }
      }
    };

    // Завершить drag на mouseup
    const handleMouseUp = () => {
      if (isDragging.value) {
        isDragging.value = false;
        dragStartIdx.value = null;
        dragMode.value = null;
        selectedRowsBeforeDrag.value = [];
        emit('row-selected', selectedRows.value);
      }
    };

    // Добавить listener для mouseup на document
    if (typeof window !== 'undefined') {
      document.addEventListener('mouseup', handleMouseUp);
    }

    // Очистить listener при unmount
    onUnmounted(() => {
      if (typeof window !== 'undefined') {
        document.removeEventListener('mouseup', handleMouseUp);
      }
    });

    return {
      palette,
      currentPage,
      sortKey,
      sortOrder,
      selectedRows,
      paginatedData,
      totalPages,
      allSelected,
      sortBy,
      toggleRow,
      toggleSelectAll,
      prevPage,
      nextPage,
      formatValue,
      onCheckboxMouseDown,
      onCheckboxMouseOver,
      getRowId,
    };
  },
};
</script>
