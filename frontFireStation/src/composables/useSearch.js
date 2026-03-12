import { ref, computed } from "vue";

/**
 * Composable для поиска и фильтрации элементов
 * @param {Ref} items - ref со списком элементов для поиска
 * @param {Array<string>} searchFields - названия полей для поиска
 * @returns {Object} - searchQuery и filtered computed
 */
export function useSearch(items, searchFields = []) {
  const searchQuery = ref("");

  const filtered = computed(() => {
    if (!searchQuery.value.trim()) {
      return items.value;
    }

    const query = searchQuery.value.toLowerCase();
    return items.value.filter((item) => {
      return searchFields.some((field) => {
        const value = item[field];
        if (value === null || value === undefined) return false;
        return String(value).toLowerCase().includes(query);
      });
    });
  });

  return {
    searchQuery,
    filtered,
  };
}
