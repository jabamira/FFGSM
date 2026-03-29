/**
 * Определения полей для форм с ограничениями из моделей
 * Используется для отображения требований при заполнении
 */

export const fieldDefinitions = {
  // User fields

  // User fields for creation (password required)
  userCreate: {
    name: {
      label: "Имя",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    surname: {
      label: "Фамилия",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    last_name: {
      label: "Отчество",
      required: false,
      maxLength: 40,
      hint: "До 40 символов",
    },
    login: {
      label: "Логин",
      required: true,
      maxLength: 15,
      unique: true,
      onlyLatinAndSpecial: true,
      hint: "До 15 символов, латиница, цифры и символы (- _ .), уникальный",
    },
    password: {
      label: "Пароль",
      required: true,
      minLength: 6,
      noKyrillic: true,
      hint: "Минимум 6 символов, латиница, цифры и спецсимволы",
    },
    phone: {
      label: "Телефон",
      required: false,
      minLength: 11,
      maxLength: 11,
      unique: true,
      onlyDigits: true,
      hint: "11 цифр, уникальный",
    },
    driver_license: {
      label: "Водительское удостоверение",
      required: false,
      minLength: 10,
      maxLength: 10,
      unique: true,
      onlyDigits: true,
      hint: "10 цифр, уникальное (обязательно для водителей)",
    },
    role: {
      label: "Роль",
      required: false,
      hint: "Выберите роль пользователя",
    },
  },

  // User fields for editing (password optional)
  userEdit: {
    name: {
      label: "Имя",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    surname: {
      label: "Фамилия",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    last_name: {
      label: "Отчество",
      required: false,
      maxLength: 40,
      hint: "До 40 символов",
    },
    login: {
      label: "Логин",
      required: true,
      maxLength: 15,
      unique: true,
      onlyLatinAndSpecial: true,
      hint: "До 15 символов, латиница, цифры и символы (- _ .), уникальный",
    },
    password: {
      label: "Пароль",
      required: false,
      minLength: 6,
      hint: "Минимум 6 символов, латиница (оставьте пустым, чтобы не менять)",
    },
    phone: {
      label: "Телефон",
      required: false,
      minLength: 11,
      maxLength: 11,
      unique: true,
      onlyDigits: true,
      hint: "11 цифр, уникальный",
    },
    driver_license: {
      label: "Водительское удостоверение",
      required: false,
      minLength: 10,
      maxLength: 10,
      unique: true,
      onlyDigits: true,
      hint: "10 цифр, уникальное (обязательно для водителей)",
    },
    role: {
      label: "Роль",
      required: false,
      hint: "Выберите роль пользователя",
    },
  },
  driverEdit: {
    name: {
      label: "Имя",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    surname: {
      label: "Фамилия",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    last_name: {
      label: "Отчество",
      required: false,
      maxLength: 40,
      hint: "До 40 символов",
    },
    login: {
      label: "Логин",
      required: true,
      maxLength: 15,
      unique: true,
      onlyLatinAndSpecial: true,
      hint: "До 15 символов, латиница, цифры и символы (- _ .), уникальный",
    },
    password: {
      label: "Пароль",
      required: false,
      minLength: 6,
      noKyrillic: true,
      hint: "Минимум 6 символов, латиница (оставьте пустым, чтобы не менять)",
    },
    phone: {
      label: "Телефон",
      required: false,
      minLength: 11,
      maxLength: 11,
      unique: true,
      onlyDigits: true,
      hint: "11 цифр, уникальный",
    },
    driver_license: {
      label: "Водительское удостоверение",
      required: true,
      minLength: 10,
      maxLength: 10,
      unique: true,
      onlyDigits: true,
      hint: "10 цифр, обязательное, уникальное",
    },
    role: {
      label: "Роль",
      required: false,
      hint: "Выберите роль пользователя",
    },
  },
  // Driver fields (для водителей - driver_license обязателен)
  driverCreate: {
    name: {
      label: "Имя",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    surname: {
      label: "Фамилия",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    last_name: {
      label: "Отчество",
      required: false,
      maxLength: 40,
      hint: "До 40 символов",
    },
    login: {
      label: "Логин",
      required: true,
      maxLength: 15,
      unique: true,
      onlyLatinAndSpecial: true,
      hint: "До 15 символов, латиница, цифры и символы (- _ .), уникальный",
    },
    password: {
      label: "Пароль",
      required: true,
      minLength: 6,
      noKyrillic: true,
      hint: "Минимум 6 символов, латиница",
    },
    phone: {
      label: "Телефон",
      required: false,
      minLength: 11,
      maxLength: 11,
      unique: true,
      onlyDigits: true,
      hint: "11 цифр, уникальный",
    },
    driver_license: {
      label: "Водительское удостоверение",
      required: true,
      minLength: 10,
      maxLength: 10,
      unique: true,
      onlyDigits: true,
      hint: "10 цифр, обязательное, уникальное",
    },
    role: {
      label: "Роль",
      required: false,
      hint: "Выберите роль пользователя",
    },
  },

  // Role fields
  role: {
    name: {
      label: "Название роли",
      required: true,
      maxLength: 50,
      unique: true,
      hint: "До 50 символов, уникальное название",
    },
  },

  // PassengerCar fields
  passengerCar: {
    number: {
      label: "Гос. номер",
      required: true,
      maxLength: 9,
      unique: true,
      hint: "До 9 символов, уникальный",
    },
    brand: {
      label: "Марка",
      required: true,
      maxLength: 60,
      hint: "До 60 символов",
    },
    model: {
      label: "Модель",
      required: true,
      maxLength: 60,
      hint: "До 60 символов",
    },
  },

  // FireTruck fields
  fireTruck: {
    number: {
      label: "Гос. номер",
      required: true,
      maxLength: 9,
      unique: true,
      hint: "До 9 символов, уникальный",
    },
    brand: {
      label: "Марка",
      required: true,
      maxLength: 60,
      hint: "До 60 символов",
    },
    model: {
      label: "Модель",
      required: true,
      maxLength: 60,
      hint: "До 60 символов",
    },
    type: {
      label: "Тип",
      required: true,
      maxLength: 60,
      hint: "До 60 символов",
    },
  },

  // NormsPassengerCars fields
  normsPassengerCars: {
    season: {
      label: "Сезон",
      required: true,
      hint: "Выберите зиму или лето",
    },
    city_norm: {
      label: "Норма по городу (л/км)",
      required: true,
      type: "decimal",
      minValue: 0,
      maxDigits: 4,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    area_norm: {
      label: "Норма по области (л/км)",
      required: true,
      type: "decimal",
      minValue: 0,
      maxDigits: 4,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    date: {
      label: "Дата утверждения",
      required: true,
      type: "date",
      hint: "Укажите дату утверждения нормы",
    },
  },

  // NormsFireTrucks fields
  normsFireTrucks: {
    season: {
      label: "Сезон",
      required: true,
      hint: "Выберите зиму или лето",
    },
    with_pump_norm: {
      label: "Норма с насосом (л/мин)",
      required: false,
      type: "decimal",
      minValue: 0,
      maxDigits: 4,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    without_pump_norm: {
      label: "Норма без насоса (л/мин)",
      required: false,
      type: "decimal",
      minValue: 0,
      maxDigits: 4,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    km_norm: {
      label: "Норма по пробегу (л/км)",
      required: false,
      type: "decimal",
      minValue: 0,
      maxDigits: 4,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    date: {
      label: "Дата утверждения",
      required: true,
      type: "date",
      hint: "Укажите дату утверждения нормы",
    },
  },

  // Waybill Record fields (используется для пассажирских и пожарных автомобилей)
  waybillRecord: {
    target: {
      label: "Цель выезда",
      required: true,
      maxLength: 255,
      hint: "До 255 символов",
    },
    departure_time: {
      label: "Время убытия",
      required: true,
      type: "time",
      hint: "Укажите время в формате HH:MM",
    },
    arrival_time: {
      label: "Время прибытия",
      required: true,
      type: "time",
      hint: "Укажите время в формате HH:MM",
    },
    distance_city_km: {
      label: "Км по городу",
      required: true,
      type: "integer",
      minValue: 0,
      maxValue: 999999,
      onlyDigits: true,
      hint: "Только цифры, максимум 999999",
    },
    distance_area_km: {
      label: "Км по области",
      required: true,
      type: "integer",
      minValue: 0,
      maxValue: 999999,
      onlyDigits: true,
      hint: "Только цифры, максимум 999999",
    },
    fuel_refueled: {
      label: "Заправка (л)",
      required: false,
      type: "decimal",
      minValue: 0,
      maxDigits: 6,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    fuel_used: {
      label: "Израсходовано топлива (л)",
      required: true,
      type: "decimal",
      minValue: 0,
      maxDigits: 6,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
  },

  // Waybill fields (путевой лист)
  passengerCarWaybill: {
    date: {
      label: "Дата путевого листа",
      required: true,
      type: "date",
      hint: "Укажите дату путевого листа",
    },
    norm_season: {
      label: "Сезон нормы",
      required: true,
      hint: "Выберите зиму или лето",
    },
    fuel_type: {
      label: "Тип топлива",
      required: true,
      hint: "Выберите тип топлива",
    },
  },

  fireTruckWaybill: {
    date: {
      label: "Дата путевого листа",
      required: true,
      type: "date",
      hint: "Укажите дату путевого листа",
    },
    norm_season: {
      label: "Сезон нормы",
      required: true,
      hint: "Выберите зиму или лето",
    },
    fuel_type: {
      label: "Тип топлива",
      required: true,
      hint: "Выберите тип топлива",
    },
  },

  // Odometer and Fuel records
  odometerFuel: {
    odometer: {
      label: "Показания одометра (км)",
      required: true,
      type: "integer",
      minValue: 0,
      maxValue: 999999,
      onlyDigits: true,
      hint: "Только цифры, максимум 999999",
    },
    fuel: {
      label: "Остаток топлива (л)",
      required: true,
      type: "decimal",
      minValue: 0,
      maxDigits: 6,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    date: {
      label: "Дата состояния",
      required: true,
      type: "date",
      hint: "Укажите дату",
    },
  },

  // Technical Maintenance fields
  technicalMaintenance: {
    date: {
      label: "Дата",
      required: true,
      type: "date",
      hint: "Укажите дату ТО",
    },
    maintenance_type: {
      label: "Вид ТО",
      required: true,
      hint: "Выберите вид технического обслуживания",
    },
    spent: {
      label: "Израсходовано",
      required: true,
      type: "decimal",
      minValue: 0,
      maxDigits: 9,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    received: {
      label: "Получено",
      required: true,
      type: "decimal",
      minValue: 0,
      maxDigits: 9,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
    operating_hours: {
      label: "Моточасы на момент ТО",
      required: true,
      type: "decimal",
      minValue: 0,
      maxDigits: 12,
      decimalPlaces: 3,
      hint: "Минимум 0, до 3 знаков после запятой/точки",
    },
  },
};

/**
 * Получить определение поля
 * @param {string} entityType - тип сущности (user, role, passengerCar и т.д.)
 * @param {string} fieldName - название поля
 * @returns {object|null} определение поля или null
 */
export function getFieldDefinition(entityType, fieldName) {
  return fieldDefinitions[entityType]?.[fieldName] || null;
}

/**
 * Получить подсказку для поля
 * @param {string} entityType - тип сущности
 * @param {string} fieldName - название поля
 * @returns {string} подсказка или пустая строка
 */
export function getFieldHint(entityType, fieldName) {
  return getFieldDefinition(entityType, fieldName)?.hint || "";
}

/**
 * Проверить, является ли поле обязательным
 * @param {string} entityType - тип сущности
 * @param {string} fieldName - название поля
 * @returns {boolean}
 */
export function isFieldRequired(entityType, fieldName) {
  return getFieldDefinition(entityType, fieldName)?.required || false;
}
