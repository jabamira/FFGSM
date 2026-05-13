# 🏗️ Структура приложения Fire Station Management System

## 📋 ТЕКУЩЕЕ СОСТОЯНИЕ (Development)

### Твоя архитектура прямо сейчас:

```
┌─ ЛОКАЛЬНАЯ СЕТЬ (администратор) ────────────────────┐
│                                                     │
│  ПОЛЬЗОВАТЕЛЬ 1 (Admin на ПК)                      │
│  ├─ Браузер: http://192.168.x.x:5173 (или localhost)
│  └─ БЫСТРО (LAN - <1ms задержка)                   │
│                                                     │
│  ПОЛЬЗОВАТЕЛЬ 2 (Бух на ноутбуке)                  │
│  ├─ Браузер: http://192.168.x.x:5173               │
│  └─ БЫСТРО (LAN - <1ms задержка)                   │
│                                                     │
│  ┌─ BACKEND СЕРВЕР (в локальной сети) ────┐       │
│  │ Django на http://192.168.x.x:8000/api   │       │
│  │ ├─ DEBUG = True                         │       │
│  │ ├─ ALLOWED_HOSTS = ['*']                │       │
│  │ └─ Запускается: python manage.py runserver      │       │
│  │                                         │       │
│  │ ┌─ DATABASE (тоже в сети) ────┐        │       │
│  │ │ PostgreSQL на 192.168.x.x:5432        │       │
│  │ │ БД: fire_station                      │       │
│  │ │ Пользователь: postgres                │       │
│  │ │ Пароль: 0632                          │       │
│  │ └─────────────────────────────┘        │       │
│  └─────────────────────────────────────────┘       │
│                                                     │
└─────────────────────────────────────────────────────┘
                      ↑
        (LAN кабель или WiFi внутри офиса)
                      ↓
┌─ ИНТЕРНЕТ (Мобильное приложение) ──────────────────┐
│                                                    │
│  ПОЛЬЗОВАТЕЛЬ 3 (Водитель на дороге)              │
│  ├─ Android/iOS приложение                        │
│  └─ МЕДЛЕННО (Интернет - 100-500ms задержка)      │
│     └─ Может быть 4G, может быть 3G/LTE           │
│                                                    │
│  Запросы идут на:                                 │
│  └─ http://192.168.x.x:8000/api (через интернет) │
│     или https://example.com/api (если деплой)    │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 🚀 КАК ВСЕ ЗАПУСКАЕТСЯ

### Терминал 1: Frontend Web

```bash
$ cd frontFireStation
$ npm run dev

# Результат:
# ✓ Vite dev server started
# ✓ http://localhost:5173
# ✓ Hot Module Replacement (HMR) включен
```

**Что происходит:**
- Vite компилирует Vue файлы в real-time
- Любое изменение кода → автоматический refresh браузера
- Source maps активны для отладки
- Все запросы идут на localhost:8000/api

---

### Терминал 2: Frontend Mobile

```bash
$ cd mobileFireStation
$ npm run dev

# Результат:
# ✓ Vite dev server started
# ✓ http://localhost:3000
# ✓ Ionic framework initialized
```

**Что происходит:**
- Запускается Ionic dev сервер
- WebView эмулирует мобильное устройство
- DevTools для отладки на мобиле
- Capacitor plugins доступны (Camera, Geolocation и т.д.)

---

### Терминал 3: Backend Django

```bash
$ cd serverFireStation/fire_station_project
$ python manage.py runserver 0.0.0.0:8000

# Результат:
# Django development server started at http://127.0.0.1:8000
# Quit the server with CONTROL-C
```

**Что происходит:**
- Django слушает порт 8000
- Любое изменение Python кода → автоматический restart
- SQL запросы логируются в консоль (DEBUG = True)
- CORS разрешает запросы с localhost:5173 и localhost:3000
- Доступен Django Admin на http://localhost:8000/admin

---

## 🔄 ПОЛНЫЙ ЦИКЛ: От клика пользователя до БД

### Пример: Получение списка пожарных машин

```
ШАГ 1: Пользователь открывает браузер
═══════════════════════════════════════════
URL: http://localhost:5173

Браузер загружает:
├─ index.html (от Vite)
├─ main.js (Vue приложение)
├─ CSS стили
└─ Другие ресурсы


ШАГ 2: Vue приложение инициализируется
═══════════════════════════════════════════
1. createApp(App)           ← Создать Vue приложение
2. createPinia()            ← State management
3. createRouter()           ← Маршрутизация
4. app.mount('#app')        ← Монтировать в DOM

Проверка авторизации:
├─ localStorage.getItem('access')
├─ Если есть → auth.isAuthenticated = true
└─ Если нет → router.push('/auth')


ШАГ 3: Компонент VehicleList монтируется
═══════════════════════════════════════════
<template>
  <div>
    <h1>Пожарные машины</h1>
    <table>
      <tr v-for="vehicle in vehicles">
        <td>{{ vehicle.number }}</td>
        <td>{{ vehicle.brand }}</td>
      </tr>
    </table>
  </div>
</template>

onMounted() → fetchVehicles()


ШАГ 4: Frontend отправляет HTTP запрос
═══════════════════════════════════════════
axios.get('/fire-trucks/', {
  headers: {
    'Authorization': 'Bearer eyJhbGc...',
    'Content-Type': 'application/json'
  }
})

Что отправляется:
┌─────────────────────────────────────────┐
│ GET /api/fire-trucks/ HTTP/1.1          │
│ Host: localhost:8000                    │
│ Authorization: Bearer eyJhbGc...        │
│ Content-Type: application/json          │
│                                         │
│ (тело пусто для GET)                   │
└─────────────────────────────────────────┘


ШАГ 5: Django получает запрос
═══════════════════════════════════════════
[Порт :8000 получил запрос]

URL Router определяет:
├─ URL: /api/fire-trucks/
├─ Метод: GET
└─ ViewSet: FireTruckViewSet.list()

Обработка:
├─ Проверка Authorization header
├─ Декодирование JWT токена
├─ Определение пользователя
├─ Проверка разрешения (view_fire_truck)
└─ Вызов метода list()


ШАГ 6: Django выполняет SQL запрос
═════════════════════════════════════════════
Django ORM преобразует в SQL:

SELECT * FROM fuel_truck 
WHERE user_id = 5 AND deleted_at IS NULL
ORDER BY number

↓ Отправляется в PostgreSQL


ШАГ 7: PostgreSQL обрабатывает запрос
═════════════════════════════════════════════
[Порт :5432 получил SQL]

1. Parse SQL syntax
2. Determine query plan
3. Use indexes (если есть)
4. Scan fuel_truck table
5. Filter по условиям
6. Вернуть результаты

SELECT результат:
┌────┬──────┬────────┬────────┬────────┐
│ id │number│ brand  │ model  │ status │
├────┼──────┼────────┼────────┼────────┤
│ 1  │ ПМ-01│ Isuzu  │  FVR   │ active │
│ 2  │ ПМ-02│ Volvo  │  FM    │ active │
│ 3  │ ПМ-03│ Isuzu  │ CXZ    │ maint. │
└────┴──────┴────────┴────────┴────────┘


ШАГ 8: Django сериализует ответ
════════════════════════════════════════════
Python объекты → JSON

{
  "results": [
    {
      "id": 1,
      "number": "ПМ-01",
      "brand": "Isuzu",
      "model": "FVR",
      "status": "active"
    },
    ...
  ],
  "count": 3,
  "next": null
}


ШАГ 9: Django отправляет HTTP ответ
═════════════════════════════════════════════
┌─────────────────────────────────────────┐
│ HTTP/1.1 200 OK                         │
│ Content-Type: application/json          │
│ Content-Length: 234                     │
│ Allow: GET, POST, HEAD, OPTIONS         │
│                                         │
│ {                                       │
│   "results": [...],                     │
│   "count": 3,                           │
│   "next": null                          │
│ }                                       │
└─────────────────────────────────────────┘


ШАГ 10: Frontend получает ответ
═════════════════════════════════════════════
response.status = 200
response.data = { results: [...], count: 3 }

Обработка:
├─ vehicles.value = response.data.results
├─ Сохранение в компоненте state
├─ Триггер Vue reactivity
└─ Re-render таблицы


ШАГ 11: Vue рендерит таблицу
═════════════════════════════════════════════
<table>
  <tr v-for="vehicle in vehicles">
    <td>1</td>
    <td>ПМ-01</td>
    <td>Isuzu</td>
    <td>FVR</td>
    <td>active</td>
  </tr>
  ... (ещё 2 машины)
</table>


ШАГ 12: Пользователь видит результат
═════════════════════════════════════════════
╔════════════════════════════════════════╗
║  Пожарные машины                       ║
╠════════════════════════════════════════╣
║ ID │ Номер │ Марка  │ Модель │ Статус ║
╠════╪═══════╪════════╪════════╪════════╣
║ 1  │ ПМ-01 │ Isuzu  │  FVR   │ active ║
║ 2  │ ПМ-02 │ Volvo  │  FM    │ active ║
║ 3  │ ПМ-03 │ Isuzu  │ CXZ    │ maint. ║
╚════╧═══════╧════════╧════════╧════════╝

✅ ГОТОВО!
Время: ~500ms от запроса до отображения
```

---

## 🔐 Авторизация (JWT)

### Как это работает:

```
ШАГ 1: Пользователь вводит логин/пароль
────────────────────────────────────────────
Форма /auth:
┌────────────────────────────────┐
│ Логин: driver1                 │
│ Пароль: ••••••••               │
│ [Войти]                        │
└────────────────────────────────┘


ШАГ 2: Frontend отправляет POST
────────────────────────────────────────────
POST /api/auth/login/ HTTP/1.1
Host: localhost:8000

{
  "login": "driver1",
  "password": "12345",
  "client": "web"
}


ШАГ 3: Django проверяет учётные данные
────────────────────────────────────────────
1. SELECT * FROM auth_user WHERE login='driver1'
2. Проверить пароль (bcrypt hashing)
3. Если совпадает:
   └─ Сгенерировать JWT токен


ШАГ 4: Django возвращает токен
────────────────────────────────────────────
HTTP/1.1 200 OK

{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjUsImxvZ2luIjoiZHJpdmVyMSIsInJvbGUiOjMsImV4cCI6MTcxNTI1MTIwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "user": {
    "id": 5,
    "login": "driver1",
    "name": "Иван",
    "surname": "Иванов",
    "role": 3
  }
}


ШАГ 5: Frontend сохраняет токен
────────────────────────────────────────────
localStorage.setItem('access', 'eyJhbGc...')
localStorage.setItem('user', JSON.stringify(user))

axios.defaults.headers.common['Authorization'] = 'Bearer eyJhbGc...'


ШАГ 6: Все следующие запросы включают токен
────────────────────────────────────────────────
GET /api/fire-trucks/

Headers:
├─ Authorization: Bearer eyJhbGc...
└─ Content-Type: application/json


ШАГ 7: Django проверяет каждый запрос
────────────────────────────────────────────
1. Получить token из Authorization header
2. Декодировать JWT
3. Проверить подпись
4. Проверить истечение (exp)
5. Определить пользователя
6. Установить request.user = User object


ШАГ 8: Health check (каждые 10 сек)
────────────────────────────────────────────
GET /api/auth/me/

Ответ:
┌─────────────────────────────────┐
│ HTTP/1.1 200 OK                 │
│                                 │
│ {                               │
│   "id": 5,                      │
│   "login": "driver1",           │
│   "name": "Иван",               │
│   "role": 3                     │
│ }                               │
│                                 │
│ Значит: токен живой ✓           │
└─────────────────────────────────┘
```

---

## 📁 Структура приложения

### Frontend Web (frontFireStation/)

```
src/
├── App.vue                    # Корневой компонент
├── main.js                    # Инициализация Vue + Pinia + Router
├── views/                     # Страницы
│   ├── Auth.vue              # Форма входа
│   ├── FuelReport.vue        # Отчеты ГСМ
│   ├── VehicleManagement.vue # Управление машинами
│   └── ...
├── components/                # Переиспользуемые компоненты
│   ├── HeaderComponent.vue
│   ├── NavigationMenu.vue
│   ├── FireTruckEditModal.vue
│   └── ...
├── router/
│   └── navigation.js          # Конфигурация маршрутов
├── stores/
│   └── auth.js               # Pinia хранилище (авторизация)
├── composables/
│   ├── useFormSubmit.js      # Логика отправки форм
│   └── useSearch.js          # Логика поиска
└── config/
    └── fieldDefinitions.js   # Конфигурация форм
```

### Backend Django (serverFireStation/)

```
fire_station_project/
├── fire_station_project/
│   ├── settings.py           # Django конфигурация
│   ├── urls.py              # Главные маршруты
│   ├── wsgi.py              # WSGI приложение
│   └── asgi.py              # ASGI для WebSocket (если нужно)
│
├── fuel/                      # Django приложение
│   ├── models.py            # Модели БД
│   │   ├── User
│   │   ├── FireTruck
│   │   ├── PassengerCar
│   │   ├── Waybill
│   │   └── ...
│   ├── views.py             # ViewSets (REST API)
│   │   ├── AuthViewSet
│   │   ├── FireTruckViewSet
│   │   ├── UserViewSet
│   │   └── ...
│   ├── serializers.py       # Сериализаторы (JSON)
│   │   ├── FireTruckSerializer
│   │   ├── UserSerializer
│   │   └── ...
│   ├── urls.py              # Маршруты приложения
│   ├── permissions.py       # Проверки разрешений
│   ├── auth.py              # JWT аутентификация
│   └── admin.py             # Django Admin
│
├── manage.py                 # Управление Django
└── venv/                     # Виртуальное окружение Python
```

### Database (PostgreSQL)

```
fire_station (БД)
├── auth_user              # Пользователи
│   ├── id (PK)
│   ├── login
│   ├── password
│   ├── role
│   ├── name
│   └── ...
│
├── fuel_truck             # Пожарные машины
│   ├── id (PK)
│   ├── number
│   ├── brand
│   ├── model
│   ├── status
│   └── ...
│
├── passenger_car          # Легковые машины
│   ├── id (PK)
│   ├── number
│   ├── ...
│
├── waybill                # Путевые листы
│   ├── id (PK)
│   ├── vehicle_id (FK)
│   ├── driver_id (FK)
│   ├── date
│   └── ...
│
└── waybill_record         # Записи путевых листов
    ├── id (PK)
    ├── waybill_id (FK)
    ├── fuel_consumed
    ├── odometer_reading
    └── ...
```

---

## 🔗 API Endpoints (текущие)

### Авторизация
```
POST   /api/auth/login/        Вход в систему
GET    /api/auth/me/           Проверка токена / текущий пользователь
```

### Пользователи
```
GET    /api/users/             Список пользователей
POST   /api/users/             Создать пользователя
GET    /api/users/{id}/        Получить пользователя
PUT    /api/users/{id}/        Обновить пользователя
DELETE /api/users/{id}/        Удалить пользователя
```

### Пожарные машины
```
GET    /api/fire-trucks/       Список машин
POST   /api/fire-trucks/       Создать машину
GET    /api/fire-trucks/{id}/  Получить машину
PUT    /api/fire-trucks/{id}/  Обновить машину
DELETE /api/fire-trucks/{id}/  Удалить машину
```

### Легковые машины
```
GET    /api/passenger-cars/    Список машин
POST   /api/passenger-cars/    Создать машину
PUT    /api/passenger-cars/{id}/  Обновить машину
DELETE /api/passenger-cars/{id}/  Удалить машину
```

### Путевые листы
```
GET    /api/fire-truck-waybills/   Список путевых листов
POST   /api/fire-truck-waybills/   Создать путевой лист
PUT    /api/fire-truck-waybills/{id}/  Обновить
DELETE /api/fire-truck-waybills/{id}/  Удалить
```

---

## 📊 Время отклика (Current Development)

### Администратор (локальная сеть - LAN)

| Операция | Время | Примечание |
|----------|-------|-----------|
| Загрузка приложения | 1-2 сек | Vue + Vite, локальная сеть |
| GET список (10-20 записей) | 50-150 ms | **⚡ БЫСТРО** - LAN |
| POST создание | 100-200 ms | Локальная сеть + БД |
| PUT обновление | 80-150 ms | **⚡ БЫСТРО** - локально |
| DELETE удаление | 50-100 ms | **⚡ БЫСТРО** - локально |
| Health check (GET /auth/me/) | 20-50 ms | Практически мгновенно |

### Водитель на дороге (мобильное приложение - интернет)

| Операция | Время | Примечание |
|----------|-------|-----------|
| Загрузка приложения | 3-5 сек | Интернет медленнее |
| GET список (10-20 записей) | 300-800 ms | **⚠️ МЕДЛЕННО** - 4G/3G/LTE |
| POST создание | 400-1000 ms | Может быть потеря сигнала |
| PUT обновление | 350-900 ms | Зависит от сигнала и location |
| DELETE удаление | 300-700 ms | **⚠️ 4G/3G/LTE задержка** |
| Health check (GET /auth/me/) | 150-400 ms | Может быть таймаут |

**Вывод:** Водитель видит задержку в 3-5 раз больше → нужна оптимизация!

---

## 🌐 Сетевая архитектура

### Сценарий 1: Администратор в офисе (локальная сеть)

```
Администратор (ПК/Ноутбук)
        ↓
    WiFi / Ethernet (LAN)
        ↓ (< 1ms задержка)
    192.168.1.100:5173 (Frontend)
        ↓
    192.168.1.100:8000/api (Backend)
        ↓
    192.168.1.100:5432 (PostgreSQL)

Все в одной локальной сети → БЫСТРО ⚡
```

**Как настроить для нескольких администраторов в офисе:**

```bash
# На сервере (где запускаешь Django)
$ python manage.py runserver 0.0.0.0:8000
# Теперь доступен на:
# - http://127.0.0.1:8000 (сам сервер, localhost)
# - http://192.168.1.100:8000 (другие компьютеры в сети)

# Узнать свой IP адрес сервера:
# Windows:  ipconfig           # Найти "IPv4 Address"
# Linux/Mac: ifconfig или ip a  # Найти "inet"
# Пример: 192.168.1.100

# Для Frontend Vite:
$ npm run dev
# По умолчанию уже слушает на 0.0.0.0
# Доступен на http://192.168.1.100:5173 с других ПК

# В браузере администратора (другой ПК в офисе):
# http://192.168.1.100:5173  <- Frontend
# API автоматически пойдет на тот же хост (192.168.1.100:8000)
```

**Преимущества:**
- Задержка < 1ms между ПК и сервером
- Все администраторы видят одни данные в real-time
- Нет зависимости от интернета
- Очень стабильно и быстро ⚡

---

### Сценарий 2: Водитель на дороге (мобильное приложение)

```
Водитель (Android/iOS)
        ↓
    Интернет (4G/3G/LTE/WiFi)
        ↓ (100-500ms задержка)
    example.com (Production сервер)
        ↓
    Backend API (https://example.com/api)
        ↓
    PostgreSQL (на сервере)

Через интернет → МЕДЛЕННЕЕ ⚠️
```

**Как будет работать в production:**
1. Администратор деплоит сервер на облако (AWS/Azure/DigitalOcean)
2. Сервер получает публичный IP и доменное имя (example.com)
3. Мобильное приложение подключается через HTTPS
4. Каждый запрос проходит через интернет (+100-500ms задержки)

---

### Сценарий 3: Гибридный (сейчас - в разработке)

```
АДМИНИСТРАТОР (локальная сеть)
    ├─ Frontend: http://192.168.x.x:5173
    ├─ Backend: http://192.168.x.x:8000/api
    └─ ⚡ БЫСТРО (~50-150ms на операцию)

ВОДИТЕЛЬ (интернет)
    ├─ Mobile app: подключается на http://192.168.x.x:8000/api
    │  (если находится в офисе или в локальной сети)
    │
    └─ Или: ⚠️ МЕДЛЕННО, если через интернет
       (~300-800ms на операцию)
```

**Проблема разработки:**
- Администратор видит быстро ⚡
- Но если тестировать мобильное приложение как реальный пользователь через интернет ⚠️ - будет медленнее

**Как тестировать:**
```
Вариант 1: Оба в одной сети
└─ Mobile app подключается на 192.168.1.100:8000
   Результат: ⚡ быстро

Вариант 2: Эмулировать медленное соединение
└─ DevTools → Network → Throttling → 3G/LTE
   Результат: ⚠️ медленно (для реальной ситуации)
```

---

Для production нужно будет:

```
ТЕКУЩЕЕ (Development)        БУДЕТ (Production)
═══════════════════════════════════════════════

Vite dev server              Nginx
:5173                        :443 (HTTPS)
                             ├─ Serve dist/
                             └─ Proxy на Django

Django runserver             Gunicorn + Supervisor
:8000                        :8000 (внутренний порт)
DEBUG = True                 DEBUG = False
CORS_ALLOW_ALL_ORIGINS=True  CORS_ALLOW_ORIGINS=['example.com']

SQLite/PostgreSQL dev        PostgreSQL production
localhost                    Отдельный сервер
DEBUG скорость важнее        Оптимизация, резервные копии


Архитектура Production:

User → HTTPS :443 (Nginx)
        ├─ Статические файлы (dist/)
        └─ Proxy → Django :8000 (interno)
                   ├─ Gunicorn (4-8 workers)
                   └─ PostgreSQL :5432 (отдельно)
```

---

## ⚡ Оптимизация для мобильного приложения (интернет)

Так как мобильные пользователи (водители) будут подключаться через интернет с задержками, нужна оптимизация:

### Проблемы медленного интернета

```
❌ Без оптимизации:
├─ Каждый клик = 300-800ms задержки
├─ Батарея телефона разряжается быстрее
├─ Плохой UX при слабом сигнале
└─ Может быть 4G/3G/LTE потери

✅ С оптимизацией:
├─ Локальное кеширование данных
├─ Работа в offline режиме
├─ Минимизация размера данных
├─ Batch запросы (несколько за раз)
├─ Компрессия JSON (gzip)
└─ Хороший UX даже при медленном интернете
```

### Что реализовать в коде

```javascript
// 1. КЕШИРОВАНИЕ на мобильном устройстве
const cache = new Map()
const CACHE_DURATION = 5 * 60 * 1000  // 5 минут

async function fetchWithCache(url) {
  // Проверить есть ли в кеше
  if (cache.has(url)) {
    console.log('📦 Из кеша:', url)
    return cache.get(url)
  }
  
  try {
    // Если нет - запросить с сервера
    const response = await axios.get(url, {
      timeout: 30000  // 30 сек таймаут (больше чем на ПК)
    })
    
    // Сохранить в кеш
    cache.set(url, response.data)
    
    // Очистить кеш через 5 минут
    setTimeout(() => cache.delete(url), CACHE_DURATION)
    
    return response.data
  } catch (error) {
    console.error('❌ Ошибка запроса:', error)
    throw error
  }
}

// 2. OFFLINE РЕЖИМ
if (!navigator.onLine) {
  console.log('📡 Нет интернета - используем локальные данные')
  // Показать кешированные данные
  // Заблокировать операции создания/обновления
}

// 3. RETRY при таймауте
axios.interceptors.response.use(null, async (error) => {
  // Если истек таймаут - повторить запрос
  if (error.code === 'ECONNABORTED') {
    console.log('⏱️ Таймаут - повторяем запрос...')
    return axios.request(error.config)
  }
  
  // Если сервер недоступен - повторить
  if (!error.response || error.response.status >= 500) {
    console.log('🔄 Сервер недоступен - повторяем...')
    await new Promise(resolve => setTimeout(resolve, 2000))  // Подождать 2 сек
    return axios.request(error.config)
  }
  
  return Promise.reject(error)
})

// 4. BATCH запросы (отправить несколько операций сразу)
async function batchUpdate(operations) {
  // Вместо 10 отдельных PUT запросов - отправить 1 batch запрос
  return axios.post('/api/batch/', {
    operations: operations  // [ {op: 'PUT', resource: 'fire-trucks/1', data: {...}}, ... ]
  })
}

// 5. МИНИМИЗАЦИЯ размера
axios.defaults.headers.common['Accept-Encoding'] = 'gzip'

// Pagination - запрашивать меньше записей
const pageSize = 10  // Вместо 20 для мобильного
```

### Тестирование медленного интернета

```
Chrome DevTools:
1. Откройте DevTools (F12)
2. Перейти на вкладку Network
3. Найти dropdown "No throttling"
4. Выбрать "Slow 3G" или "Fast 3G"
5. Отправить запрос - увидите реальную задержку ⚠️

Пример реальных времен:
├─ No throttling: 50-150ms
├─ Fast 3G: 300-400ms ✓ (большинство водителей)
├─ Slow 3G: 500-800ms ⚠️ (плохой сигнал)
└─ Offline: Использовать кеш или показать ошибку
```

---

## 📋 Текущие параметры

| Параметр | Значение | Файл |
|----------|----------|------|
| DEBUG | True | settings.py:L30 |
| CORS | Allow all origins | settings.py:L32 |
| Database | PostgreSQL | settings.py:L87 |
| DB Host | localhost | settings.py:L90 |
| DB Port | 5432 | settings.py:L92 |
| DB Name | fire_station | settings.py:L88 |
| DB User | postgres | settings.py:L89 |
| JWT Auth | ✓ JWTAuthentication | settings.py:L98 |
| Frontend URL | localhost:5173 | - |
| Backend URL | localhost:8000 | - |
| Mobile URL | localhost:3000 | - |

---

## ✅ Резюме

```
Как это работает ПРЯМО СЕЙЧАС:

АДМИНИСТРАТОР В ОФИСЕ (локальная сеть)
═══════════════════════════════════════════════════════
1. Запускаешь 3 терминала (Vite + Ionic + Django)
2. Frontend Web слушает :5173 (локально)
3. Mobile Web слушает :3000 (локально)
4. Backend слушает :8000 (в локальной сети)
5. База данных на :5432 (в сети)

Производительность: ⚡ БЫСТРО
├─ GET список: 50-150ms (практически мгновенно)
├─ POST/PUT: 100-200ms
└─ Пользователь видит результат сразу


ВОДИТЕЛЬ НА ДОРОГЕ (мобильное приложение)
═══════════════════════════════════════════════════════
6. Мобильное приложение подключается через интернет
7. Запросы идут на production сервер (когда будет деплой)
8. Все через HTTPS

Производительность: ⚠️ МЕДЛЕННЕЕ
├─ GET список: 300-800ms (с задержкой)
├─ POST/PUT: 400-1000ms
└─ Нужна оптимизация (кеширование, offline режим)


АВТОРИЗАЦИЯ (общее для всех):
═════════════════════════════════════════════════════════
├─ JWT токен хранится в localStorage/Device Storage
├─ Отправляется в Authorization header
├─ Django проверяет на каждый запрос
└─ Health check каждые 10 секунд


KEY DIFFERENCE:
═════════════════════════════════════════════════════════
Admin (локальная сеть):  50-200ms per request ⚡ FAST
Водитель (интернет):     300-800ms per request ⚠️ SLOW
                         (нужна оптимизация!)
```

---

**Создано:** 9 мая 2026  
**Версия:** 1.0 (Development setup)  
**Статус:** Активная разработка
