/**
 * Константы для типов топлива
 * Ключ - значение из базы данных, значение - человекочитаемое отображение
 */
export const FUEL_TYPES = {
  petrol95: "Бензин (АИ-95)",
  petrol92: "Бензин (АИ-92)",
  diesel: "Дизельное топливо",
};

/**
 * Массив опций для SelectInput
 */
export const fuelTypeOptions = [
  { value: "petrol95", label: FUEL_TYPES.petrol95 },
  { value: "petrol92", label: FUEL_TYPES.petrol92 },
  { value: "diesel", label: FUEL_TYPES.diesel },
];

/**
 * Получить человекочитаемое название типа топлива
 */
export const formatFuelType = (fuelType) => {
  return FUEL_TYPES[fuelType] || fuelType;
};
