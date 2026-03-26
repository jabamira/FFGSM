/**
 * Utility functions for error handling and validation
 */

/**
 * Parse Django REST Framework error response
 * @param {Object} error - axios error object
 * @returns {Object} parsed error with formatted messages
 */
export function parseApiError(error) {
  if (!error.response) {
    return {
      title: "Network Error",
      message: error.message || "Unable to reach the server",
      fieldErrors: [],
    };
  }

  const data = error.response.data;
  const fieldErrors = [];

  if (typeof data === "object") {
    Object.entries(data).forEach(([field, messages]) => {
      if (field !== "detail" && field !== "message") {
        const messageText = Array.isArray(messages)
          ? messages.join(", ")
          : String(messages);
        fieldErrors.push({
          field: formatFieldName(field),
          message: messageText,
        });
      }
    });
  }

  return {
    title: error.response.status === 400 ? "Validation Error" : "Error",
    message: data.detail || data.message || "Operation failed",
    fieldErrors,
    statusCode: error.response.status,
  };
}

/**
 * Convert snake_case field names to readable Russian names
 * @param {string} fieldName - field name in snake_case
 * @returns {string} formatted field name
 */
export function formatFieldName(fieldName) {
  const fieldMap = {
    name: "Имя",
    surname: "Фамилия",
    last_name: "Отчество",
    login: "Логин",
    password: "Пароль",
    phone: "Телефон",
    driver_license: "Водительское удостоверение",
    role: "Роль",
    number: "Номер",
    brand: "Марка",
    model: "Модель",
    season: "Сезон",
    city_norm: "Норма по городу",
    area_norm: "Норма по области",
    target: "Цель выезда",
    departure_time: "Время убытия",
    arrival_time: "Время прибытия",
    distance_city_km: "Км по городу",
    distance_area_km: "Км по области",
    fuel_refueled: "Заправка",
    fuel_used: "Израсходовано топлива",
  };

  return (
    fieldMap[fieldName] ||
    fieldName.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase())
  );
}

/**
 * Validate form data against field definitions
 * @param {Object} data - form data to validate
 * @param {Object} definitions - field definitions from fieldDefinitions.js
 * @returns {Object} validation errors object {fieldName: errorMessage}
 */
export function validateFormFields(data, definitions) {
  const errors = {};

  Object.entries(definitions).forEach(([fieldName, fieldDef]) => {
    const value = data[fieldName];

    // Check required
    if (fieldDef.required && !value) {
      errors[fieldName] = "Обязательное поле";
      return;
    }

    // Skip further validation if no value
    if (!value) return;

    const strValue = String(value).trim();
    const numValue = Number(value);

    // Check onlyDigits constraint - only numbers allowed
    if (fieldDef.onlyDigits && !/^\d+$/.test(strValue.replace(/\s/g, ""))) {
      errors[fieldName] = "Допускаются только цифры";
      return;
    }

    // Check onlyLatinAndSpecial constraint - only latin letters, numbers, and special chars (- _ .)
    if (fieldDef.onlyLatinAndSpecial && !/^[a-zA-Z0-9._-]+$/.test(strValue)) {
      errors[fieldName] =
        "Допускаются латинские буквы, цифры и символы (- _ .)";
      return;
    }

    // Check noKyrillic constraint - no cyrillic letters allowed
    if (fieldDef.noKyrillic && /[а-яА-ЯёЁ]/.test(strValue)) {
      errors[fieldName] = "Кириллица не допускается";
      return;
    }

    // Check maxLength for strings
    if (fieldDef.maxLength && strValue.length > fieldDef.maxLength) {
      errors[fieldName] =
        `Максимум ${fieldDef.maxLength} символов (введено ${strValue.length})`;
    }

    // Check minLength for strings
    if (fieldDef.minLength && strValue.length < fieldDef.minLength) {
      errors[fieldName] = `Минимум ${fieldDef.minLength} символов`;
    }

    // Validate email format if type is email
    if (fieldDef.type === "email" && !isValidEmail(strValue)) {
      errors[fieldName] = "Некорректный формат email";
    }

    // Note: phone validation with only digits will be handled by onlyDigits check above

    // Validate decimal number format (with . or , as separator)
    if (fieldDef.type === "decimal" && strValue) {
      if (!/^\d+([.,]\d+)?$/.test(strValue)) {
        errors[fieldName] =
          "Используйте формат числа (точка или запятая как разделитель)";
        return;
      }
      // Normalize separator for further validation (convert comma to dot)
      const normalizedValue = strValue.replace(",", ".");
      const numValueDecimal = Number(normalizedValue);
      if (isNaN(numValueDecimal)) {
        errors[fieldName] = "Должно быть числом";
        return;
      }
    }

    // Validate number ranges
    if (fieldDef.type === "integer" || fieldDef.type === "decimal") {
      // For decimal, normalize the separator
      let checkValue = numValue;
      if (fieldDef.type === "decimal" && strValue) {
        const normalizedValue = strValue.replace(",", ".");
        checkValue = Number(normalizedValue);
      }

      if (isNaN(checkValue)) {
        errors[fieldName] = "Должно быть числом";
      } else {
        // Check minValue
        if (fieldDef.minValue !== undefined && checkValue < fieldDef.minValue) {
          errors[fieldName] = `Минимальное значение: ${fieldDef.minValue}`;
        }
        // Check maxValue
        if (fieldDef.maxValue !== undefined && checkValue > fieldDef.maxValue) {
          errors[fieldName] = `Максимальное значение: ${fieldDef.maxValue}`;
        }
        // Check decimal places for decimal fields
        if (
          fieldDef.type === "decimal" &&
          fieldDef.decimalPlaces !== undefined
        ) {
          const normalizedValue = strValue.replace(",", ".");
          const decimalPart = normalizedValue.split(".")[1];
          if (decimalPart && decimalPart.length > fieldDef.decimalPlaces) {
            errors[fieldName] =
              `Максимум ${fieldDef.decimalPlaces} знаков после запятой`;
          }
        }
      }
    }

    // Check maxDigits for decimal fields
    if (fieldDef.type === "decimal" && fieldDef.maxDigits && strValue) {
      const normalizedValue = strValue.replace(",", ".");
      const digitsOnly = normalizedValue.replace(/\./g, "");
      if (digitsOnly.length > fieldDef.maxDigits) {
        errors[fieldName] = `Максимум ${fieldDef.maxDigits} цифр`;
      }
    }

    // Check time format (HH:MM)
    if (
      fieldDef.type === "time" &&
      strValue &&
      !/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(strValue)
    ) {
      errors[fieldName] = "Формат должен быть HH:MM";
    }
  });

  return errors;
}

/**
 * Check if there are any validation errors
 * @param {Object} errors - validation errors object
 * @returns {boolean}
 */
export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}

/**
 * Get error message for specific field
 * @param {Object} errors - validation errors
 * @param {string} fieldName - field name
 * @returns {string} error message or empty string
 */
export function getFieldError(errors, fieldName) {
  return errors[fieldName] || "";
}

/**
 * Convert validation errors to axios error format for ErrorModal
 * @param {Object} errors - validation errors from validateFormFields
 * @param {string} mainMessage - main error message
 * @returns {Object} error object format for ErrorModal.openModal()
 */
export function createValidationError(
  errors,
  mainMessage = "Ошибка валидации",
) {
  const error = new Error(mainMessage);
  const data = {
    detail: mainMessage,
    ...errors,
  };
  error.response = { data };
  return error;
}

/**
 * Simple email validation
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}
