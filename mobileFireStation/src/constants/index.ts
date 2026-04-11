/**
 * Типы топлива
 */
export const FUEL_TYPES = {
  GASOLINE: 'gasoline',
  DIESEL: 'diesel',
  GAS: 'gas',
  LPG: 'lpg',
  ELECTRIC: 'electric',
}

export const FUEL_TYPES_LABELS = {
  [FUEL_TYPES.GASOLINE]: 'Бензин',
  [FUEL_TYPES.DIESEL]: 'Дизель',
  [FUEL_TYPES.GAS]: 'Газ',
  [FUEL_TYPES.LPG]: 'ГСМ',
  [FUEL_TYPES.ELECTRIC]: 'Электро',
}

/**
 * Статусы путевых листов
 */
export const WAYBILL_STATUS = {
  DRAFT: 'draft',
  PENDING: 'pending',
  COMPLETED: 'completed',
  REJECTED: 'rejected',
}

export const WAYBILL_STATUS_LABELS = {
  [WAYBILL_STATUS.DRAFT]: 'Черновик',
  [WAYBILL_STATUS.PENDING]: 'На проверке',
  [WAYBILL_STATUS.COMPLETED]: 'Завершено',
  [WAYBILL_STATUS.REJECTED]: 'Отклонено',
}

/**
 * Роли пользователей
 */
export const USER_ROLES = {
  DRIVER: 'driver',
  MANAGER: 'manager',
  ADMIN: 'admin',
}

export const USER_ROLES_LABELS = {
  [USER_ROLES.DRIVER]: 'Водитель',
  [USER_ROLES.MANAGER]: 'Менеджер',
  [USER_ROLES.ADMIN]: 'Администратор',
}
