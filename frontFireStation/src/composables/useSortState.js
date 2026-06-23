import { ref, watch } from "vue";

/**
 * Composable для управления состоянием сортировки таблицы
 * Автоматически сохраняет и восстанавливает состояние из localStorage
 *
 * @param {string} tableName - Уникальное имя таблицы для localStorage
 * @returns {Object} { sortBy, sortOrder, setSortOrder, loadSortState, saveSortState }
 */
export function useSortState(tableName) {
  const sortBy = ref("");
  const sortOrder = ref("asc"); // 'asc' или 'desc'

  const STORAGE_KEY = `table_sort_${tableName}`;

  // Загрузить состояние сортировки из localStorage
  const loadSortState = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const { sortBy: savedSortBy, sortOrder: savedSortOrder } =
          JSON.parse(stored);
        sortBy.value = savedSortBy || "";
        sortOrder.value = savedSortOrder || "asc";
        console.log(`[useSortState] Loaded sort state for ${tableName}:`, {
          sortBy: sortBy.value,
          sortOrder: sortOrder.value,
        });
      }
    } catch (error) {
      console.error(
        `[useSortState] Error loading sort state for ${tableName}:`,
        error,
      );
    }
  };

  // Сохранить состояние сортировки в localStorage
  const saveSortState = () => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          sortBy: sortBy.value,
          sortOrder: sortOrder.value,
        }),
      );
      console.log(`[useSortState] Saved sort state for ${tableName}:`, {
        sortBy: sortBy.value,
        sortOrder: sortOrder.value,
      });
    } catch (error) {
      console.error(
        `[useSortState] Error saving sort state for ${tableName}:`,
        error,
      );
    }
  };

  // Установить порядок сортировки и сохранить
  const setSortOrder = (newSortBy, newSortOrder = "asc") => {
    sortBy.value = newSortBy;
    sortOrder.value = newSortOrder;
    saveSortState();
  };

  // Смотрим за изменениями и сохраняем
  watch([sortBy, sortOrder], () => {
    saveSortState();
  });

  return {
    sortBy,
    sortOrder,
    setSortOrder,
    loadSortState,
    saveSortState,
  };
}
