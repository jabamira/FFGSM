<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
 

    <div class="max-w-7xl mx-auto px-4 py-12">
      <!-- Page Header -->
      <div class="mb-12">
        <h1 class="text-4xl font-bold mb-3" :style="{ color: palette.dark }">UI Компоненты</h1>
        <p class="text-lg" :style="{ color: palette.medium }">
          Полный справочник всех доступных компонентов с примерами кастомизации
        </p>
      </div>

      <!-- Button Component -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">Button (Кнопка)</h2>

        <!-- Button Variants -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.secondary }">Варианты</h3>
          <div class="flex flex-wrap gap-3">
            <Button variant="primary" label="Primary" />
            <Button variant="secondary" label="Secondary" />
            <Button variant="danger" label="Danger" />
            <Button variant="success" label="Success" />
            <Button variant="outline" label="Outline" />
            <Button variant="ghost" label="Ghost" />
          </div>
        </div>

        <!-- Button Sizes -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.secondary }">Размеры</h3>
          <div class="flex flex-wrap gap-3 items-center">
            <Button size="xs" label="Extra Small" />
            <Button size="sm" label="Small" />
            <Button size="md" label="Medium" />
            <Button size="lg" label="Large" />
            <Button size="xl" label="Extra Large" />
          </div>
        </div>

        <!-- Button States -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.secondary }">Состояния</h3>
          <div class="flex flex-wrap gap-3">
            <Button variant="primary" label="Normal" />
            <Button variant="primary" label="Disabled" disabled />
            <Button variant="primary" label="Loading..." :loading="true" />
            <Button variant="primary" label="Full Width" fullWidth />
            <Button variant="primary" label="Rounded" rounded />
          </div>
        </div>

        <!-- Code Example -->
        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
          <pre>&lt;Button
  variant="primary"
  size="lg"
  label="Начать"
  @click="handleClick"
  :loading="isLoading"
  :disabled="isDisabled"
  fullWidth
/&gt;</pre>
        </div>
      </section>

      <!-- TextInput Component -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">TextInput (Текстовое поле)</h2>

        <div class="grid md:grid-cols-2 gap-8 mb-8">
          <TextInput
            v-model="inputDemo.text"
            label="Обычное поле"
            placeholder="Введите текст"
            hint="Это вспомогательный текст"
          />
          <TextInput
            v-model="inputDemo.email"
            type="email"
            label="Email"
            placeholder="user@example.com"
            error="Некорректный email адрес"
          />
          <TextInput
            v-model="inputDemo.number"
            type="number"
            label="Число"
            placeholder="0"
          />
          <TextInput
            v-model="inputDemo.password"
            type="password"
            label="Пароль"
            placeholder="••••••••"
            required
          />
          <TextInput
            v-model="inputDemo.disabled"
            label="Отключенное"
            placeholder="Невозможно редактировать"
            disabled
          />
          <TextInput
            v-model="inputDemo.date"
            type="date"
            label="Дата"
          />
        </div>

        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
          <pre>&lt;TextInput
  v-model="email"
  type="email"
  label="Email"
  placeholder="user@example.com"
  error="Invalid email"
  required
/&gt;</pre>
        </div>
      </section>

      <!-- SelectInput Component -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">SelectInput (Выбор)</h2>

        <div class="grid md:grid-cols-2 gap-8 mb-8">
          <SelectInput
            v-model="selectDemo.product"
            label="Тип ГСМ"
            :options="productTypes"
            placeholder="Выберите тип"
          />
          <SelectInput
            v-model="selectDemo.status"
            label="Статус"
            :options="statusOptions"
            error="Поле обязательно"
            required
          />
          <SelectInput
            v-model="selectDemo.disabled"
            label="Отключенный"
            :options="productTypes"
            disabled
          />
        </div>

        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
          <pre>&lt;SelectInput
  v-model="productType"
  label="Product Type"
  :options="[
    { value: 'oil', label: 'Motor Oil' },
    { value: 'coolant', label: 'Engine Coolant' }
  ]"
  placeholder="Select a product"
/&gt;</pre>
        </div>
      </section>

      <!-- Alert Component -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">Alert (Уведомление)</h2>

        <div class="space-y-4 mb-8">
          <Alert
            type="success"
            title="Успешно!"
            message="Операция выполнена успешно. Все данные сохранены."
            :closeable="false"
          />
          <Alert
            type="error"
            title="Ошибка"
            message="Что-то пошло не так. Пожалуйста, попробуйте снова."
            :closeable="false"
          />
          <Alert
            type="warning"
            title="Внимание"
            message="Это действие не может быть отменено. Продолжить?"
            :closeable="false"
          />
          <Alert
            type="info"
            title="Информация"
            message="Это полезная информация для вас. Нажмите ✕ для закрытия."
          />
        </div>

        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
          <pre>&lt;Alert
  type="success"
  title="Saved!"
  message="Changes saved successfully."
  :closeable="false"
/&gt;</pre>
        </div>
      </section>

      <!-- Badge Component -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">Badge (Бейдж)</h2>

        <!-- Filled Badges -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.secondary }">Заполненные</h3>
          <div class="flex flex-wrap gap-3">
            <Badge label="Default" />
            <Badge type="success" label="Active" />
            <Badge type="error" label="Inactive" />
            <Badge type="warning" label="Pending" />
            <Badge type="info" label="Info" />
            <Badge type="primary" label="Primary" />
          </div>
        </div>

        <!-- Outline Badges -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.secondary }">Контуры</h3>
          <div class="flex flex-wrap gap-3">
            <Badge label="Default" outline />
            <Badge type="success" label="Active" outline />
            <Badge type="error" label="Inactive" outline />
            <Badge type="warning" label="Pending" outline />
            <Badge type="primary" label="Primary" outline />
          </div>
        </div>

        <!-- Sizes -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.secondary }">Размеры</h3>
          <div class="flex flex-wrap gap-3 items-center">
            <Badge type="primary" label="Small" size="sm" />
            <Badge type="primary" label="Medium" size="md" />
            <Badge type="primary" label="Large" size="lg" />
          </div>
        </div>

        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
          <pre>&lt;Badge type="success" label="Active" /&gt;
&lt;Badge type="warning" label="Pending" outline /&gt;
&lt;Badge type="primary" label="Primary" size="lg" /&gt;</pre>
        </div>
      </section>

      <!-- Modal Component -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">Modal (Модальное окно)</h2>

        <Button
          variant="primary"
          label="Открыть модальное окно"
          @click="showDemoModal = true"
          class="mb-8"
        />

        <Modal
          :is-open="showDemoModal"
          title="Пример модального окна"
          confirm-label="Сохранить"
          @close="showDemoModal = false"
          @confirm="showDemoModal = false"
        >
          <div class="space-y-4">
            <p :style="{ color: palette.dark }">Это содержимое модального окна.</p>
            <TextInput
              v-model="modalInput"
              label="Поле ввода"
              placeholder="Введите данные"
            />
            <p class="text-sm" :style="{ color: palette.medium }">
              Вы можете добавить любое содержимое внутрь модального окна, включая формы, таблицы и другие компоненты.
            </p>
          </div>
        </Modal>

        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
          <pre>&lt;Modal
  :is-open="showModal"
  title="Confirm Action"
  confirm-label="Delete"
  @close="showModal = false"
  @confirm="handleDelete"
&gt;
  &lt;p&gt;Are you sure?&lt;/p&gt;
&lt;/Modal&gt;</pre>
        </div>
      </section>

      <!-- DataTable Component -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">DataTable (Таблица данных)</h2>

        <div class="mb-4">
          <h3 class="text-lg font-semibold mb-4" :style="{ color: palette.secondary }">Таблица с сортировкой и пагинацией</h3>
        </div>

        <DataTable
          :data="tableData"
          :columns="tableColumns"
          :actions="tableActions"
          selectable
          paginate
          page-size="5"
        >
          <template #cell-status="{ value }">
            <Badge
              :type="value === 'В наличии' ? 'success' : 'warning'"
              :label="value"
            />
          </template>
        </DataTable>

        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto mt-8">
          <pre>&lt;DataTable
  :data="products"
  :columns="[
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'price', label: 'Price', type: 'currency' }
  ]"
  :actions="[
    { name: 'edit', label: 'Edit', event: 'edit-row' }
  ]"
  selectable
  paginate
  @edit-row="editProduct"
/&gt;</pre>
        </div>
      </section>

      <!-- Theme Customization -->
      <section class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6" :style="{ color: palette.dark }">Кастомизация темы</h2>

        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold mb-3" :style="{ color: palette.secondary }">Текущая палитра цветов</h3>
            <div class="grid md:grid-cols-3 gap-4">
              <div class="p-4 rounded-lg text-white text-center font-semibold" style="background-color: #405267">
                Dark #405267
              </div>
              <div class="p-4 rounded-lg text-white text-center font-semibold" style="background-color: #7C91A6">
                Medium #7C91A6
              </div>
              <div class="p-4 rounded-lg text-white text-center font-semibold" style="background-color: #4A99B2">
                Primary #4A99B2
              </div>
              <div class="p-4 rounded-lg text-white text-center font-semibold" style="background-color: #4486A5">
                Secondary #4486A5
              </div>
              <div class="p-4 rounded-lg text-gray-800 text-center font-semibold" style="background-color: #AFB1B4">
                Light #AFB1B4
              </div>
              <div class="p-4 rounded-lg text-white text-center font-semibold" style="background-color: #E74C3C">
                Error #E74C3C
              </div>
            </div>
          </div>

          <div>
            <h3 class="text-lg font-semibold mb-3" :style="{ color: palette.secondary }">Редактирование темы</h3>
            <p class="mb-4" :style="{ color: palette.medium }">
              Все цвета определены в файле <code class="bg-gray-100 px-2 py-1 rounded">src/components/ui/theme.js</code>
            </p>
            <div class="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
              <pre>// src/components/ui/theme.js
export const palette = {
  dark: "#405267",
  medium: "#7C91A6",
  primary: "#4A99B2",
  secondary: "#4486A5",
  light: "#AFB1B4",
  error: "#E74C3C",
  success: "#27AE60",
  warning: "#F39C12",
};</pre>
            </div>
          </div>
        </div>
      </section>

      <!-- Back Button -->
      <div class="flex gap-3 justify-center mb-8">
        <Button
          variant="outline"
          label="← Вернуться на главную"
          @click="() => $router.push('/')"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import HeaderComponent from '../components/HeaderComponent.vue';
import { Button, TextInput, SelectInput, Alert, Badge, Modal, DataTable, palette } from '../components/ui/importUi';

export default {
  name: 'UIComponentsPage',
  components: {
    HeaderComponent,
    Button,
    TextInput,
    SelectInput,
    Alert,
    Badge,
    Modal,
    DataTable,
  },
  setup() {
    const inputDemo = ref({
      text: '',
      email: '',
      number: '',
      password: '',
      disabled: 'Отключено',
      date: '',
    });

    const selectDemo = ref({
      product: '',
      status: '',
      disabled: '',
    });

    const productTypes = [
      { value: 'oil', label: 'Масло моторное' },
      { value: 'transmission', label: 'Трансмиссионное масло' },
      { value: 'coolant', label: 'Охлаждающая жидкость' },
      { value: 'brake', label: 'Тормозная жидкость' },
    ];

    const statusOptions = [
      { value: 'active', label: 'Активный' },
      { value: 'inactive', label: 'Неактивный' },
      { value: 'pending', label: 'В ожидании' },
    ];

    const tableData = [
      { id: 1, name: 'Масло 5W-30', quantity: 150, price: 24.99, status: 'В наличии' },
      { id: 2, name: 'ATF Transmission', quantity: 45, price: 35.50, status: 'В наличии' },
      { id: 3, name: 'Engine Coolant', quantity: 200, price: 12.75, status: 'В наличии' },
      { id: 4, name: 'Brake Fluid', quantity: 0, price: 18.99, status: 'Отсутствует' },
      { id: 5, name: 'Power Steering', quantity: 80, price: 28.50, status: 'В наличии' },
      { id: 6, name: 'Differential Oil', quantity: 60, price: 31.75, status: 'В наличии' },
    ];

    const tableColumns = [
      { key: 'id', label: 'ID' },
      { key: 'name', label: 'Название' },
      { key: 'quantity', label: 'Кол-во' },
      { key: 'price', label: 'Цена', type: 'currency' },
      { key: 'status', label: 'Статус' },
    ];

    const tableActions = [
      { name: 'edit', label: '✎ Редактировать', event: 'edit-row' },
      { name: 'delete', label: '✕ Удалить', event: 'delete-row', color: palette.error },
    ];

    const showDemoModal = ref(false);
    const modalInput = ref('');

    return {
      inputDemo,
      selectDemo,
      productTypes,
      statusOptions,
      tableData,
      tableColumns,
      tableActions,
      showDemoModal,
      modalInput,
      palette,
    };
  },
};
</script>
