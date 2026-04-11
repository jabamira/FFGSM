# 🚀 Fire Station Mobile - Ionic приложение для водителей

Полнофункциональное мобильное приложение для управления путевыми листами и отчетами о топливе, разработанное на Vue 3 + Ionic + Capacitor с адаптацией под мобильные устройства.

## 📱 Возможности

✅ **Аутентификация** - Безопасный вход через email/пароль  
✅ **Путевые листы** - Просмотр, создание и управление путевыми листами  
✅ **Отчеты о топливе** - Быстрое добавление отчетов о заправках  
✅ **Поиск и фильтрация** - Удобный поиск по путевым листам  
✅ **Настройки профиля** - Управление профилем и уведомлениями  
✅ **Оффлайн поддержка** - Работает и без интернета (кэширование)  
✅ **Поддержка Android и iOS** - Один код для двух платформ  

## 🎯 Быстрый старт

### 1️⃣ Установка зависимостей

```bash
cd mobileFireStation
npm install
```

### 2️⃣ Запуск в браузере

```bash
npm run dev
```

Откроется на http://localhost:5174

### 3️⃣ Тестирование на устройстве

```bash
# Собрать приложение
npm run build

# Для Android
npm run android

# Для iOS (только на Mac)
npm run ios
```

## 📁 Структура проекта

```
mobileFireStation/
├── src/
│   ├── api/                    # API клиент и endpoints
│   │   ├── client.ts           # Axios инстанс
│   │   └── index.ts            # Все endpoints
│   │
│   ├── pages/                  # Страницы приложения
│   │   ├── LoginPage.vue
│   │   ├── DriverDashboard.vue
│   │   ├── WaybillListPage.vue
│   │   ├── WaybillDetailPage.vue
│   │   ├── FuelReportPage.vue
│   │   └── SettingsPage.vue
│   │
│   ├── components/             # Vue компоненты
│   │   ├── modals/
│   │   ├── forms/
│   │   └── shared/
│   │
│   ├── stores/                 # Pinia хранилище
│   │   ├── auth.ts
│   │   └── waybill.ts
│   │
│   ├── router/
│   │   └── index.ts            # Vue Router конфиг
│   │
│   ├── types/                  # TypeScript типы
│   ├── utils/                  # Утилиты и helpers
│   ├── constants/              # Константы и перечисления
│   ├── composables/            # Переиспользуемые логики
│   │
│   ├── App.vue
│   └── main.ts
│
├── package.json
├── vite.config.ts
├── ionic.config.json
├── capacitor.config.ts
└── tsconfig.json
```

## 🔌 API Endpoints

Приложение использует следующие endpoint'ы:

### Аутентификация
- `POST /api/auth/login/` - Вход в приложение
- `POST /api/auth/logout/` - Выход
- `GET /api/auth/profile/` - Получить профиль
- `PATCH /api/auth/profile/` - Обновить профиль

### Путевые листы
- `GET /api/waybills/` - Список путевых листов
- `GET /api/waybills/{id}/` - Получить путевой лист
- `POST /api/waybills/` - Создать путевой лист
- `PUT /api/waybills/{id}/` - Обновить путевой лист
- `DELETE /api/waybills/{id}/` - Удалить путевой лист
- `POST /api/waybills/{id}/complete/` - Завершить путевой лист

### Отчеты о топливе
- `GET /api/fuel-reports/` - Список отчетов
- `POST /api/fuel-reports/` - Создать отчет
- `PUT /api/fuel-reports/{id}/` - Обновить отчет
- `DELETE /api/fuel-reports/{id}/` - Удалить отчет

## 💻 Использование API

### В компонентах Vue

```typescript
<script setup lang="ts">
import { api } from '@/api'
import { getErrorMessage } from '@/utils'

const loadWaybills = async () => {
  try {
    const response = await api.waybill.list()
    waybills.value = response.data.results
  } catch (error: any) {
    const msg = getErrorMessage(error)
    console.error(msg)
  }
}
</script>
```

### Работа с формами

```typescript
import { useFormSubmit } from '@/composables'

const { isLoading, error, fieldErrors, submit } = useFormSubmit(
  async (data) => await api.fuel.create(data)
)

const handleSubmit = async () => {
  await submit({ liters: 50, cost: 3000 })
}
```

### Типизация данных

```typescript
import type { User, Waybill, FuelReport } from '@/types'

interface MyData {
  user: User
  waybills: Waybill[]
  reports: FuelReport[]
}
```

### Константы и метки

```typescript
import { WAYBILL_STATUS_LABELS, FUEL_TYPES_LABELS } from '@/constants'

const statusLabel = WAYBILL_STATUS_LABELS['completed'] // 'Завершено'
const fuelLabel = FUEL_TYPES_LABELS['diesel'] // 'Дизель'
```

## 🎨 Стилизация

Приложение использует комбинацию:
- **Ionic CSS** - базовые мобильные компоненты
- **Tailwind CSS** - утилиты для стилей

### Пример стилизации

```vue
<template>
  <div class="flex flex-col items-center p-4">
    <h1 class="text-2xl font-bold mb-4">Заголовок</h1>
    <ion-button color="primary" expand="block">Кнопка</ion-button>
  </div>
</template>
```

## 📦 Зависимости

- **Vue 3** - Фреймворк
- **Ionic/Vue** - UI компоненты
- **Capacitor** - Доступ к нативным возможностям
- **Tailwind CSS** - Утилиты для стилей
- **Axios** - HTTP клиент
- **Pinia** - Управление состоянием
- **TypeScript** - Типизация

## 🔐 Безопасность

- Токены автоматически добавляются в заголовок `Authorization`
- При истечении токена (401) пользователь перенаправляется на вход
- Все запросы идут через HTTPS в продакшене
- CORS настроен на backend

## 🚀 Развертывание

### Android

```bash
npm run build
npm run android

# В Android Studio:
# 1. Build → Generate Signed Bundle/APK
# 2. Загрузить в Google Play Console
```

### iOS

```bash
npm run build
npm run ios

# В Xcode:
# 1. Product → Archive
# 2. Загрузить через Transporter
```

## 🧪 Тестирование

### Браузер
```bash
npm run dev  # F12 → Console для отладки
```

### Android устройство
```bash
# Chrome DevTools
chrome://inspect
```

### iOS устройство
```bash
# Safari Web Inspector
```

## 📚 Документация

- [GETTING_STARTED.md](../GETTING_STARTED.md) - Полный чек-лист
- [QUICK_START.md](../QUICK_START.md) - Быстрые команды
- [MOBILE_DEVELOPMENT_GUIDE.md](../MOBILE_DEVELOPMENT_GUIDE.md) - Архитектура
- [PROJECT_ARCHITECTURE.md](../PROJECT_ARCHITECTURE.md) - Диаграммы

## 🆘 Решение проблем

### Приложение не запускается

```bash
# Очистить кеш
rm -rf node_modules
npm install
npm run dev
```

### Ошибки при сборке

```bash
# Пересинхронизировать Capacitor
npx capacitor sync
```

### Проблемы с токеном

```typescript
// Проверить токен в localStorage
console.log(localStorage.getItem('auth_token'))

// Очистить при выходе
localStorage.removeItem('auth_token')
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте консоль браузера (F12)
2. Проверьте, что backend работает на http://localhost:8000
3. Убедитесь, что Node.js версия 16+

## 📈 Улучшения

- [ ] Добавить GPS отслеживание маршрута
- [ ] Настроить push-уведомления
- [ ] Добавить фото квитанций
- [ ] Оффлайн синхронизация
- [ ] Тёмный режим
- [ ] Интеграция с календарём

## 📄 Лицензия

Проект Fire Station Mobile

---

**Начните разработку: `npm run dev`** 🎉

