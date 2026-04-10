/**
 * Преобразует дату из ISO формата (YYYY-MM-DD) в русский формат (ДД.MM.YYYY)
 * @param {string} isoDate - Дата в ISO формате (YYYY-MM-DD)
 * @returns {string} - Дата в русском формате (ДД.MM.YYYY)
 */
export const formatDateToRussian = (isoDate) => {
  if (!isoDate) return "";
  const [year, month, day] = isoDate.split("-");
  return `${day}.${month}.${year}`;
};

/**
 * Преобразует дату из русского формата (ДД.MM.YYYY) в ISO формат (YYYY-MM-DD)
 * @param {string} russianDate - Дата в русском формате (ДД.MM.YYYY)
 * @returns {string} - Дата в ISO формате (YYYY-MM-DD)
 */
export const formatDateToISO = (russianDate) => {
  if (!russianDate) return "";
  const [day, month, year] = russianDate.split(".");
  return `${year}-${month}-${day}`;
};
