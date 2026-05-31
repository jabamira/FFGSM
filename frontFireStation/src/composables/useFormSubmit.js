import { ref } from "vue";

/**
Не используется пока что, но может быть полезен для обработки форм и отображения ошибок в модальном окне
 */
export function useFormSubmit() {
  const errorModalRef = ref(null);

  /**
   * Обработать ошибку и показать в модальном окне
   * @param {Error} error - ошибка
   */
  const handleError = (error) => {
    if (errorModalRef.value) {
      errorModalRef.value.openModal(error);
    } else {
      console.error("ErrorModal ref not set:", error);
    }
  };

  /**
   * Обработать успешный запрос
   * Закрыть модали, показать уведомление
   */
  const handleSuccess = (message = "Данные успешно сохранены") => {
    // TODO: интегрировать с уведомлениями
    console.log(message);
  };

  /**
   * Установить ссылку на ErrorModal
   */
  const setErrorModalRef = (ref) => {
    errorModalRef.value = ref;
  };

  return {
    errorModalRef,
    handleError,
    handleSuccess,
    setErrorModalRef,
  };
}
