import { ref, reactive, computed } from 'vue'
import { getErrorMessage, getFormErrors } from './index'

export const useFormSubmit = (submitFn) => {
  const isLoading = ref(false)
  const error = ref('')
  const fieldErrors = reactive({})

  const submit = async (data) => {
    isLoading.value = true
    error.value = ''
    Object.keys(fieldErrors).forEach(key => delete fieldErrors[key])

    try {
      const response = await submitFn(data)
      return response
    } catch (err) {
      error.value = getErrorMessage(err)
      const errors = getFormErrors(err)
      Object.assign(fieldErrors, errors)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearErrors = () => {
    error.value = ''
    Object.keys(fieldErrors).forEach(key => delete fieldErrors[key])
  }

  return {
    isLoading,
    error,
    fieldErrors,
    submit,
    clearErrors,
  }
}

export const useSearch = (items, searchFields) => {
  const searchQuery = ref('')

  const filteredItems = computed(() => {
    if (!searchQuery.value) return items

    return items.filter(item =>
      searchFields.some(field =>
        String(item[field]).toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    )
  })

  return {
    searchQuery,
    filteredItems,
  }
}
