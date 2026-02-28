<template>
  <footer :style="{ borderTop: `1px solid ${palette.light}`, background: palette.white }" class="w-full">
    <div class="max-w-7xl mx-auto px-4 py-6">
      <div class="grid md:grid-cols-3 gap-6 items-start">
        <div class="flex items-start gap-3">
          <svg width="56" height="56" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <circle :fill="palette.primary" cx="24" cy="24" r="22" />
            <text x="24" y="30" text-anchor="middle" :style="{ fill: palette.white, fontWeight: '700', fontSize: '14px' }">ПСЧ</text>
          </svg>
          <div>
            <div :style="{ color: palette.dark, fontWeight: 700 }">ПСЧ МЧС 37</div>
            <div class="text-sm mt-1" :style="{ color: palette.medium }">Адрес: г. Сыктывкар, ул. Примерная, 1</div>
            <div class="text-sm" :style="{ color: palette.medium }">Телефон: +7 (8212) 34-56-78</div>
            <div class="text-sm" :style="{ color: palette.medium }">E-mail: info@mchs37.ru</div>
          </div>
        </div>

        <div class="md:col-span-2 flex flex-col md:flex-row md:justify-end gap-6">
          <div>
            <h4 class="font-semibold mb-2" :style="{ color: palette.dark }">О ведомстве</h4>
            <ul class="text-sm" :style="{ color: palette.medium }">
              <li class="mb-1"><a href="#" class="hover:underline">О подразделении</a></li>
              <li class="mb-1"><a href="#" class="hover:underline">Услуги</a></li>
              <li class="mb-1"><a href="#" class="hover:underline">Контакты</a></li>
            </ul>
          </div>

          <div class="text-right md:text-right">
            <h4 class="font-semibold mb-2" :style="{ color: palette.dark }">Полезная информация</h4>
            <ul class="text-sm" :style="{ color: palette.medium }">
              <li class="mb-1"><a href="#" class="hover:underline">Политика конфиденциальности</a></li>
              <li class="mb-1"><a href="#" class="hover:underline">Лицензии</a></li>
            </ul>
          </div>
        </div>
      </div>

      <hr class="my-4" :style="{ borderColor: palette.light }" />

      <div class="flex flex-col md:flex-row md:justify-between items-center gap-2">
        <span class="text-sm" :style="{ color: palette.medium }">© {{ year }} ПСЧ МЧС 37. Все права защищены.</span>
        <span class="text-sm" :style="{ color: palette.medium }">Разработано: Отдел ИТ</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref } from 'vue';
import { palette } from './ui/theme.js';

const year = new Date().getFullYear();
</script>

<style scoped></style>
