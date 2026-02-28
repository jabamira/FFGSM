<template>
  <div class="overflow-x-auto rounded-lg border" :style="{ borderColor: palette.light }">
    <table class="w-full border-collapse">
      <!-- Table Header -->
      <thead>
        <tr :style="{ backgroundColor: `${palette.primary}15`, borderColor: palette.light, borderBottomWidth: '1px' }">
          <th class="w-12 px-4 py-3 text-left">
            <input
              v-if="selectable"
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
          class="border-b hover:opacity-75"
          :style="{ borderColor: palette.light, backgroundColor: idx % 2 === 0 ? 'white' : `${palette.light}10` }"
        >
          <td class="w-12 px-4 py-3">
            <input
              v-if="selectable"
              type="checkbox"
              :checked="selectedRows.includes(idx)"
              @change="toggleRow(idx)"
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
      <p>No data available</p>
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
import { ref, computed } from 'vue';
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
    paginate: {
      type: Boolean,
      default: true,
    },
    pageSize: {
      type: Number,
      default: 10,
    },
  },
  emits: ['row-selected', 'sort', 'edit-row', 'delete-row', 'view-row'],
  setup(props, { emit }) {
    const currentPage = ref(1);
    const sortKey = ref(null);
    const sortOrder = ref('asc');
    const selectedRows = ref([]);

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
      const index = selectedRows.value.indexOf(idx);
      if (index > -1) {
        selectedRows.value.splice(index, 1);
      } else {
        selectedRows.value.push(idx);
      }
      emit('row-selected', selectedRows.value);
    };

    const toggleSelectAll = () => {
      if (allSelected.value) {
        selectedRows.value = [];
      } else {
        selectedRows.value = paginatedData.value.map((_, idx) => idx);
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
    };
  },
};
</script>
