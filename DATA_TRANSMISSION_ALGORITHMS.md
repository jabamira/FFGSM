# 4.4.2 Алгоритмы использования технологий передачи данных

## 📡 Обзор технологий передачи данных

### Стек используемых технологий

| Технология | Версия | Назначение | Статус |
|-----------|--------|-----------|--------|
| **HTTP/HTTPS** | 1.1 | Протокол передачи данных | Основной |
| **REST API** | - | Архитектура API | Основная |
| **JSON** | - | Формат данных | Основной |
| **Axios** | 1.8.4 | HTTP клиент | Основной |
| **JWT** | - | Авторизация | Основная |
| **Bearer Token** | - | Передача токена | Основная |
| **localStorage** | - | Хранение данных | Вспомогательная |

---

## 1️⃣ АЛГОРИТМ ОБЩЕНИЯ С СЕРВЕРОМ

### 1.1 Архитектура запроса-ответа

```
┌──────────────┐
│   Frontend   │ (Vue 3 приложение)
│   (Client)   │
└──────┬───────┘
       │
       │ Axios Request
       │ ├─ URL: http://localhost:8000/api/...
       │ ├─ Method: GET/POST/PUT/DELETE
       │ ├─ Headers: Authorization: Bearer {token}
       │ ├─ Query Params: ?filter=value
       │ └─ Body: JSON data
       │
       ▼
┌──────────────────────────┐
│  HTTP/HTTPS Transport    │
│  (TCP/IP Port 8000)      │
└──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Backend (Django REST Framework) │
│ ├─ URL Router                   │
│ ├─ ViewSet/View                 │
│ ├─ Permission Check             │
│ ├─ Business Logic               │
│ └─ Database Query               │
└──────┬──────────────────────────┘
       │
       │ Axios Response
       │ ├─ Status Code: 200/201/400/401/403/500
       │ ├─ Headers: Content-Type: application/json
       │ └─ Body: JSON response
       │
       ▼
┌──────────────┐
│   Frontend   │
│   (Client)   │
└──────────────┘
```

### 1.2 Типовая последовательность запроса

```javascript
// ШАГ 1: Инициализация запроса
const response = await axios.get(
  '/fire-trucks/',              // URL (базовый URL уже установлен)
  {
    headers: {
      'Authorization': 'Bearer eyJhbGc...',  // JWT токен
      'Content-Type': 'application/json'
    },
    timeout: 5000,              // Таймаут 5 секунд
    params: {                   // Query параметры
      'page': 1,
      'limit': 20
    }
  }
);

// ШАГ 2: Обработка ответа
if (response.status === 200) {
  const data = response.data;   // JSON данные
  // Обработать данные
}
```

### 1.3 Конфигурация Axios

```javascript
// main.js - глобальная конфигурация
import axios from "axios";

// Установка базового URL
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
axios.defaults.baseURL = API_URL;

// Глобальные параметры
axios.defaults.headers.common["Content-Type"] = "application/json";

// Таймауты
axios.defaults.timeout = 10000;  // 10 секунд
```

### 1.4 HTTP методы и их использование

| Метод | Описание | Пример | Тело запроса |
|-------|---------|--------|-------------|
| **GET** | Получить данные | `GET /fire-trucks/` | Нет |
| **POST** | Создать новый ресурс | `POST /fire-trucks/` | JSON объект |
| **PUT** | Обновить весь ресурс | `PUT /fire-trucks/1/` | JSON объект |
| **DELETE** | Удалить ресурс | `DELETE /fire-trucks/1/` | Нет |
| **PATCH** | Частичное обновление | `PATCH /fire-trucks/1/` | JSON объект (только изменённые поля) |

### 1.5 Примеры реальных запросов из приложения

#### Получение списка пожарных машин (GET)
```javascript
const response = await axios.get('fire-trucks/', {
  headers: { 'Authorization': 'Bearer {token}' },
  timeout: 5000
});

// Ответ:
{
  "results": [
    {
      "id": 1,
      "number": "ПМ-01",
      "brand": "Isuzu",
      "model": "FVR",
      "status": "active"
    },
    { "id": 2, "number": "ПМ-02", ... }
  ]
}
```

#### Создание нового водителя (POST)
```javascript
const response = await axios.post('/users/', {
  name: 'Иван',
  last_name: 'Петров',
  login: 'ivan_petrov',
  password: 'securepass123',
  role: 'driver'
}, {
  headers: { 'Authorization': 'Bearer {token}' }
});

// Ответ:
{
  "id": 5,
  "name": "Иван",
  "last_name": "Петров",
  "login": "ivan_petrov",
  "role": "driver"
}
```

#### Обновление машины (PUT)
```javascript
const response = await axios.put(`/fire-trucks/1/`, {
  number: "ПМ-01-NEW",
  brand: "Isuzu",
  model: "FVR",
  status: "maintenance"
}, {
  headers: { 'Authorization': 'Bearer {token}' }
});

// Ответ:
{
  "id": 1,
  "number": "ПМ-01-NEW",
  "brand": "Isuzu",
  "model": "FVR",
  "status": "maintenance"
}
```

#### Удаление машины (DELETE)
```javascript
await axios.delete(`/fire-trucks/1/`, {
  headers: { 'Authorization': 'Bearer {token}' }
});

// Ответ:
{
  "status": "deleted"
}
```

### 1.6 Обработка ошибок при общении

```javascript
try {
  const response = await axios.get('/fire-trucks/');
  // Успех: статус 200-299
  return response.data;
} catch (error) {
  if (!error.response) {
    // Сетевая ошибка
    console.error('Network error:', error.message);
    serverError = true;
  } else if (error.response.status === 400) {
    // Плохой запрос
    console.error('Bad request:', error.response.data);
  } else if (error.response.status === 401) {
    // Неавторизован
    console.error('Unauthorized:', error.response.data);
    logout();
  } else if (error.response.status === 403) {
    // Доступ запрещён
    console.error('Forbidden:', error.response.data);
  } else if (error.response.status === 500) {
    // Ошибка сервера
    console.error('Server error:', error.response.data);
    serverError = true;
  }
}
```

---

## 2️⃣ АЛГОРИТМ АВТОРИЗАЦИИ

### 2.1 Схема авторизации с использованием JWT

```
┌─────────────┐
│   Пользователь  │
│ вводит данные   │
│ (логин/пароль) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  POST /auth/login/      │
│  {                      │
│    login: "user123",    │
│    password: "pass123", │
│    client: "web"        │
│  }                      │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ Backend проверка учётных данных          │
│ ├─ Проверка логина/пароля в БД           │
│ ├─ Валидация пароля (bcrypt)            │
│ └─ Генерация JWT токена                  │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Ответ 200 OK                 │
│ {                            │
│   "access": "eyJhbGc...",    │ ← JWT токен
│   "user": {                  │
│     "id": 1,                 │
│     "login": "user123",      │
│     "role": "chief"          │
│   }                          │
│ }                            │
└────────┬─────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Frontend сохраняет              │
│ ├─ access → localStorage        │
│ ├─ user → localStorage          │
│ └─ access → Axios default header│
└────────┬────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Пользователь авторизован       │
│ (может использовать API)       │
└────────────────────────────────┘
```

### 2.2 JWT токен - структура

**JWT состоит из 3 частей, разделённых точками: `header.payload.signature`**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImxvZ2luIjoidXNlcjEyMyIsInJvbGUiOiJjaGllZiIsImV4cCI6MTcxNTI1MTIwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Part 1: Header (декодировано)**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Part 2: Payload (декодировано)**
```json
{
  "sub": 1,              // ID пользователя
  "login": "user123",    // Логин
  "role": "chief",       // Роль
  "exp": 1715251200,     // Время истечения (Unix timestamp)
  "iat": 1715164800      // Время создания
}
```

**Part 3: Signature**
```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret_key
)
```

### 2.3 Алгоритм входа в систему (Пошагово)

```javascript
// ШАГ 1: Пользователь нажимает кнопку "Войти"
async function login(username, password) {
  // ШАГ 2: Отправить POST запрос на сервер
  const response = await axios.post('/auth/login/', {
    login: username,
    password: password,
    client: 'web'
  });
  
  // ШАГ 3: Получить токен и данные пользователя
  const { access, user } = response.data;
  
  // ШАГ 4: Сохранить токен в localStorage
  localStorage.setItem('access', access);
  
  // ШАГ 5: Сохранить данные пользователя в localStorage
  localStorage.setItem('user', JSON.stringify(user));
  
  // ШАГ 6: Установить токен в Axios headers
  axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
  
  // ШАГ 7: Запустить периодическую проверку (health polling)
  startHealthPolling();
  
  // ШАГ 8: Загрузить разрешения пользователя
  await fetchPermissions();
  
  // ШАГ 9: Перенаправить в приложение
  router.push('/fuel-report');
  
  return true;
}
```

### 2.4 Проверка авторизации при запусе приложения

```javascript
// main.js - при инициализации приложения

// ШАГ 1: Восстановить состояние из localStorage
const auth = useAuthStore();
auth.loadFromStorage();
// Ищет в localStorage: 'access', 'user', 'permissions'

// ШАГ 2: Декодировать JWT и проверить истечение (локально)
auth.fetchUser();
// Декодирует часть payload и проверяет поле exp

// ШАГ 3: Настроить перехватчики Axios
auth.setupAxiosInterceptors();
// Если 401 → logout
// Если 403 → показать ошибку разрешения
// Если 500+ → показать ошибку сервера

// ШАГ 4: Проверить соединение с сервером
if (auth.isAuthenticated) {
  auth.checkConnection();  // GET /auth/me/
}

// ШАГ 5: Запустить периодическую проверку
// каждые 10 секунд отправляется GET /auth/me/
```

### 2.5 Перехватчики Axios (Interceptors)

```javascript
// Request Interceptor (перед отправкой)
axios.interceptors.request.use(
  (config) => {
    // ПРОВЕРКА 1: Есть ли токен?
    if (this.access) {
      // Добавить токен в заголовок Authorization
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${this.access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor (после получения ответа)
axios.interceptors.response.use(
  (response) => response,  // Успех - вернуть как есть
  (error) => {
    // ОБРАБОТКА ОШИБОК
    
    // Нет соединения
    if (!error.response) {
      serverError = true;
      router.push('/server-error');
      return Promise.reject(error);
    }
    
    // 5xx - Ошибка сервера
    if (error.response.status >= 500) {
      serverError = true;
      router.push('/server-error');
      return Promise.reject(error);
    }
    
    // 401 - Неавторизован (токен истёк или неверен)
    if (error.response.status === 401) {
      logout();  // Удалить токен
      router.push('/auth');  // На страницу входа
      return Promise.reject(error);
    }
    
    // 403 - Доступ запрещён (разрешение отсутствует)
    if (error.response.status === 403) {
      // НЕ выходить из системы!
      // Показать ошибку разрешения
      showToast('Нет прав для этого действия');
      return Promise.reject(error);
    }
    
    return Promise.reject(error);
  }
);
```

### 2.6 Health Check (Проверка живого токена)

```javascript
// Каждые 10 секунд
async function checkConnection() {
  try {
    // Отправить GET /auth/me/ для проверки
    const response = await axios.get('/auth/me/', {
      headers: { 'Authorization': `Bearer ${this.access}` },
      timeout: 5000
    });
    
    // Успех: токен живой
    if (response.data && response.data.id) {
      return true;  // Авторизован
    }
  } catch (error) {
    // Ошибка: токен истёк или сервер недоступен
    if (error.response?.status === 401) {
      logout();  // Токен истёк
    } else if (error.response?.status >= 500) {
      serverError = true;  // Сервер недоступен
    }
    return false;  // Не авторизован
  }
}
```

---

## 3️⃣ ЧТО ОЗНАЧАЕТ "ПОЛЬЗОВАТЕЛЬ АВТОРИЗОВАН"

### 3.1 Условия авторизации

Пользователь считается **авторизованным**, если выполнены **ВСЕ** условия:

| Условие | Проверка | Где хранится |
|---------|----------|-------------|
| **1. Токен присутствует** | `auth.access !== null` | localStorage + Pinia store |
| **2. Токен не истёк** | `JWT.exp > Date.now()` | Декодировано из JWT |
| **3. Токен валиден** | `GET /auth/me/` вернул 200 | Backend проверка |
| **4. Пользователь существует** | `auth.user !== null` | localStorage + Pinia store |
| **5. Соединение с сервером** | `lastVerifyResult === true` | Health check результат |

### 3.2 Проверка авторизации в коде

```javascript
// В компонентах Vue
const auth = useAuthStore();

// Способ 1: Получить статус авторизации
if (auth.isAuthenticated) {
  // Пользователь авторизован - показать приложение
  console.log('User is logged in');
} else {
  // Пользователь не авторизован - показать форму входа
  console.log('User is not logged in');
}

// Способ 2: Получить данные пользователя
if (auth.user) {
  console.log(`ID: ${auth.user.id}`);
  console.log(`Login: ${auth.user.login}`);
  console.log(`Role: ${auth.user.role}`);
}

// Способ 3: Получить токен
if (auth.access) {
  console.log(`Token: ${auth.access.substring(0, 20)}...`);
}

// Способ 4: Проверить разрешения
if (auth.permissions && auth.permissions.view_drivers) {
  // Разрешение есть - показать кнопку
}

// Способ 5: Проверить соединение с сервером
if (auth.serverError) {
  // Сервер недоступен
  console.log('Server is down');
}
```

### 3.3 Getter для проверки авторизации

```javascript
// В auth.js store
export const useAuthStore = defineStore('auth', {
  getters: {
    isAuthenticated(state) {
      // ИСТИНА, если:
      // - Токен присутствует
      // - Токен не пустой (не null, не undefined)
      return !!state.access;
    }
  }
});

// Использование в компоненте
<template>
  <div v-if="auth.isAuthenticated">
    <!-- Показать для авторизованных -->
    <p>Добро пожаловать, {{ auth.user.login }}</p>
  </div>
  <div v-else>
    <!-- Показать для неавторизованных -->
    <p>Пожалуйста, войдите в систему</p>
  </div>
</template>
```

### 3.4 Состояния авторизации

```
┌─────────────────────────────────────────────────────┐
│           ЖИЗНЕННЫЙ ЦИКЛ АВТОРИЗАЦИИ                │
└─────────────────────────────────────────────────────┘

┌─────────────────┐
│  Приложение     │
│  запустилось    │
└────────┬────────┘
         │
         ▼
    ┌─────────────┐
    │ Проверка    │
    │ localStorage│
    └────┬────────┘
         │
    ┌────────────────────┐
    │  Токен найден?     │
    └─┬──────────────┬───┘
      │ ДА           │ НЕТ
      ▼              ▼
   ┌──────────┐   ┌──────────────────┐
   │ Проверить│   │ СОСТОЯНИЕ:       │
   │ exp дату │   │ НЕ АВТОРИЗОВАН   │
   └───┬──────┘   │ Показать /auth   │
       │          └──────────────────┘
    ┌──┴──────────────┐
    │ Токен истёк?    │
    └─┬────────────┬──┘
      │ ДА (exp)   │ НЕТ
      ▼            ▼
   ┌─────────┐  ┌──────────────────┐
   │ Удалить │  │ Проверка на      │
   │ токен   │  │ сервере          │
   │ Logout  │  │ GET /auth/me/    │
   └────┬────┘  └───┬───────────┬──┘
        │           │ OK        │ Ошибка
        │           │           │ 401/403
        │           ▼           ▼
        │        ┌─────────┐  ┌──────────┐
        └───────►│ АВТОРИЗОВАН   │ Logout   │
                 │ Может работать│ и вернуть│
                 └─────────┘  │ на /auth │
                              └──────────┘
```

### 3.5 Сценарий: Потеря авторизации

```javascript
// СЦЕНАРИЙ 1: Пользователь вышел из системы
auth.logout();  // Все данные удалены
// Результат: isAuthenticated = false

// СЦЕНАРИЙ 2: Токен истёк
// Проверка: auth.decodeToken().exp < Date.now()
// Действие: auth.logout() + перенаправление на /auth
// Сообщение: "Сессия истекла, войдите заново"

// СЦЕНАРИЙ 3: Пароль изменён на другом устройстве
// Проверка: GET /auth/me/ вернул 401
// Действие: auth.logout()
// Сообщение: "Авторизуйтесь заново"

// СЦЕНАРИЙ 4: Роль изменилась (например, с admin на user)
// Проверка: auth.permissions обновлены неправильно
// Действие: Обновить разрешения в фоне
// Сообщение: Показать "Ваши разрешения обновлены"

// СЦЕНАРИЙ 5: Сервер недоступен
// Проверка: GET /auth/me/ нет соединения
// Действие: serverError = true
// Сообщение: Показать /server-error с возможностью Retry
```

---

## 4️⃣ ТИПОВЫЕ API ENDPOINTS

### Авторизация

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/auth/login/` | Вход в систему | login, password, client |
| GET | `/auth/me/` | Текущий пользователь | - |
| GET | `/permissions/current/` | Разрешения текущего | - |

### Водители

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/users/drivers/` | Список водителей |
| POST | `/users/` | Создать водителя |
| PUT | `/users/{id}/` | Обновить водителя |
| DELETE | `/users/{id}/` | Удалить водителя |

### Пожарные машины

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/fire-trucks/` | Список пожарных машин |
| POST | `/fire-trucks/` | Создать машину |
| PUT | `/fire-trucks/{id}/` | Обновить машину |
| DELETE | `/fire-trucks/{id}/` | Удалить машину |

### Легковые машины

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/passenger-cars/` | Список легковых машин |
| POST | `/passenger-cars/` | Создать машину |
| PUT | `/passenger-cars/{id}/` | Обновить машину |
| DELETE | `/passenger-cars/{id}/` | Удалить машину |

### Путевые листы

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/fire-truck-waybills/` | Путевые листы пожарных |
| POST | `/fire-truck-waybills/` | Создать путевой лист |
| PUT | `/fire-truck-waybills/{id}/` | Обновить путевой лист |
| DELETE | `/fire-truck-waybills/{id}/` | Удалить путевой лист |

### Статистика

| Метод | Endpoint | Описание |
|-------|----------|---------|
| GET | `/statistics/summary/` | Сводка расходов ГСМ |

---

## 5️⃣ КОДЫ ОТВЕТОВ HTTP

### Успешные ответы (2xx)

| Код | Статус | Значение |
|-----|--------|----------|
| **200** | OK | Успешный GET запрос |
| **201** | Created | Успешное создание (POST) |
| **204** | No Content | Успешное удаление (DELETE) |

### Ошибки клиента (4xx)

| Код | Статус | Значение | Действие |
|-----|--------|----------|----------|
| **400** | Bad Request | Неверные параметры | Показать ошибку пользователю |
| **401** | Unauthorized | Токен неверен/истёк | Logout, перейти на /auth |
| **403** | Forbidden | Нет разрешения | Показать "Доступ запрещён" |
| **404** | Not Found | Ресурс не найден | Показать ошибку 404 |

### Ошибки сервера (5xx)

| Код | Статус | Значение | Действие |
|-----|--------|----------|----------|
| **500** | Internal Error | Ошибка в коде backend | Показать /server-error |
| **502** | Bad Gateway | Сервер недоступен | Показать /server-error |
| **503** | Service Unavailable | Сервер на обслуживании | Показать /server-error |

---

## 6️⃣ ПРИМЕРЫ КОДА ДЛЯ РАЗРАБОТКИ

### Пример 1: Базовый GET запрос

```javascript
// Получить список машин
async function fetchVehicles() {
  try {
    // Запрос автоматически включит токен из Axios config
    const response = await axios.get('/fire-trucks/');
    
    // Статус 200 - успех
    return response.data.results;
  } catch (error) {
    // Автоматическая обработка через interceptor
    console.error('Error fetching vehicles:', error.message);
  }
}
```

### Пример 2: POST запрос с данными

```javascript
async function createDriver(driverData) {
  try {
    const response = await axios.post('/users/', {
      name: driverData.name,
      last_name: driverData.lastName,
      login: driverData.login,
      password: driverData.password,
      role: 'driver'
    });
    
    // Статус 201 - создано
    return response.data;
  } catch (error) {
    if (error.response?.status === 400) {
      // Ошибка валидации
      console.error('Validation error:', error.response.data);
    } else if (error.response?.status === 403) {
      // Нет разрешения
      showToast('Нет прав на создание водителя');
    }
  }
}
```

### Пример 3: Проверка авторизации в компоненте

```vue
<template>
  <div>
    <!-- Защита: показать только если авторизован -->
    <div v-if="auth.isAuthenticated">
      <h1>Добро пожаловать, {{ auth.user.login }}</h1>
      
      <!-- Дополнительная проверка разрешений -->
      <button 
        v-if="auth.permissions?.edit_drivers"
        @click="handleEdit"
      >
        Редактировать
      </button>
      
      <button @click="handleLogout">
        Выход
      </button>
    </div>
    
    <!-- Редирект на /auth если не авторизован -->
    <div v-else>
      <p>Требуется авторизация</p>
      <!-- Компонент Router автоматически перенаправит на /auth -->
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();

const handleLogout = () => {
  auth.logout();
  // Перенаправление на /auth происходит автоматически
};
</script>
```

### Пример 4: Обработка 403 ошибки (нет разрешения)

```javascript
async function deleteDriver(driverId) {
  try {
    await axios.delete(`/users/${driverId}/`);
    showToast('Водитель удалён');
  } catch (error) {
    if (error.response?.status === 403) {
      // Пользователь остаётся авторизован!
      showToast('Нет прав на удаление водителя', 'error');
      // Кнопка удаления будет отключена, когда разрешения обновятся
    } else if (error.response?.status === 401) {
      // Перенаправление на /auth происходит автоматически в interceptor
    }
  }
}
```

---

## 📊 Диаграмма полного цикла авторизации

```
ЦИКЛ 1: ПЕРВЫЙ ЗАПУСК ПРИЛОЖЕНИЯ
═══════════════════════════════════════════════════════════════
  ┌─────────────────────────────────────────────┐
  │ 1. Пользователь открывает браузер           │
  │    URL: http://localhost:3000                │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 2. main.js инициализирует приложение        │
  │    ├─ Импортирует auth store                │
  │    ├─ Проверяет localStorage                │
  │    └─ Находит ничего (первый запуск)        │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 3. Router перенаправляет на /auth           │
  │    (потому что auth.isAuthenticated = false)│
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 4. Показывается форма входа                 │
  │    ├─ Поле логина                           │
  │    ├─ Поле пароля                           │
  │    └─ Кнопка "Войти"                        │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 5. Пользователь заполняет форму и нажимает  │
  │    кнопку "Войти"                           │
  └─────────────┬───────────────────────────────┘
                ▼
  
ЦИКЛ 2: ВХОД В СИСТЕМУ
═══════════════════════════════════════════════════════════════
  ┌─────────────────────────────────────────────┐
  │ 6. auth.login('user123', 'pass123')         │
  │    ├─ POST /auth/login/                     │ ← ЗАПРОС
  │    ├─ { login, password, client }           │
  │    └─ ОТВЕТ: { access, user }               │ ← ОТВЕТ
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 7. Сохранение данных                        │
  │    ├─ localStorage.access = token           │
  │    ├─ localStorage.user = JSON              │
  │    └─ axios.headers.Authorization = Bearer  │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 8. Загрузка разрешений                      │
  │    ├─ GET /permissions/current/             │ ← ЗАПРОС
  │    ├─ localStorage.permissions = JSON       │
  │    └─ auth.permissionsLoaded = true         │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 9. Запуск health polling                    │
  │    ├─ каждые 10 сек: GET /auth/me/         │
  │    └─ Проверка живости токена              │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 10. Перенаправление в приложение            │
  │     router.push('/fuel-report')             │
  │     Состояние: АВТОРИЗОВАН ✓                │
  └─────────────┬───────────────────────────────┘
                ▼

ЦИКЛ 3: РАБОТА В ПРИЛОЖЕНИИ (каждые 10 сек)
═══════════════════════════════════════════════════════════════
  ┌─────────────────────────────────────────────┐
  │ 11. checkConnection() = верификация         │
  │     ├─ GET /auth/me/                        │ ← ЗАПРОС
  │     ├─ Ответ 200: токен живой ✓            │
  │     └─ lastVerifyResult = true              │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 12. Пользователь может:                     │
  │     ├─ Просматривать данные (GET)           │
  │     ├─ Создавать данные (POST)              │
  │     ├─ Обновлять данные (PUT)               │
  │     └─ Удалять данные (DELETE)              │
  │                                             │
  │ Все запросы включают токен автоматически   │
  └─────────────┬───────────────────────────────┘
                ▼

ЦИКЛ 4: ВЫХОД ИЗ СИСТЕМЫ
═══════════════════════════════════════════════════════════════
  ┌─────────────────────────────────────────────┐
  │ 13. Пользователь нажимает "Выход"           │
  │     auth.logout()                           │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 14. Очистка данных                          │
  │     ├─ localStorage.clear()                 │
  │     ├─ auth.access = null                   │
  │     ├─ auth.user = null                     │
  │     ├─ auth.permissions = {}                │
  │     └─ axios.headers.Authorization = delete │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 15. Остановка health polling                │
  │     clearInterval(healthIntervalId)         │
  └─────────────┬───────────────────────────────┘
                ▼
  ┌─────────────────────────────────────────────┐
  │ 16. Перенаправление на /auth                │
  │     Состояние: НЕ АВТОРИЗОВАН ✗             │
  └─────────────────────────────────────────────┘
```

---

## 🔒 Безопасность передачи данных

### Рекомендации для production

1. **Использовать HTTPS** (обязательно)
   - Все данные будут зашифрованы в пути
   - Использовать SSL сертификаты

2. **HTTP-only Cookies вместо localStorage**
   - localStorage уязвим для XSS атак
   - httpOnly cookie защищён автоматически

3. **CSRF Protection**
   - Django имеет встроенную защиту
   - Включить CSRF токены

4. **Refresh Tokens**
   - Добавить механизм обновления токенов
   - Частая смена access token

5. **Rate Limiting**
   - Ограничить количество запросов
   - Защита от brute-force атак

---

**Последнее обновление:** 9 мая 2026
