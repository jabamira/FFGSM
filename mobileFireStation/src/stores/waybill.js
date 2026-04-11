import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWaybillStore = defineStore('waybill', () => {
  const waybills = ref([])
  const currentWaybill = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const searchQuery = ref('')

  const setWaybills = (newWaybills) => {
    waybills.value = newWaybills
  }

  const setCurrentWaybill = (waybill) => {
    currentWaybill.value = waybill
  }

  const addWaybill = (waybill) => {
    waybills.value.unshift(waybill)
  }

  const updateWaybill = (id, waybill) => {
    const index = waybills.value.findIndex(w => w.id === id)
    if (index !== -1) {
      waybills.value[index] = { ...waybills.value[index], ...waybill }
    }
  }

  const deleteWaybill = (id) => {
    waybills.value = waybills.value.filter(w => w.id !== id)
  }

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const setError = (newError) => {
    error.value = newError
  }

  const setSearch = (query) => {
    searchQuery.value = query
  }

  return {
    waybills,
    currentWaybill,
    isLoading,
    error,
    searchQuery,
    setWaybills,
    setCurrentWaybill,
    addWaybill,
    updateWaybill,
    deleteWaybill,
    setLoading,
    setError,
    setSearch,
  }
})
