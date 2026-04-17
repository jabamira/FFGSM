<template>
  <ion-page class="page-layout">
    <!-- Header -->
    <ion-header :translucent="true" class="no-border">
      <ion-toolbar :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)', '--border-bottom': 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '24px' }">
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 0 16px;">
          <button @click="goBack" style="background: none; border: none; cursor: pointer; font-size: 24px;">
            ← 
          </button>
          <ion-title :style="{ color: palette.dark, textAlign: 'center', flex: 1 }">Путевой лист</ion-title>
          <div style="width: 24px;"></div>
        </div>
      </ion-toolbar>
    </ion-header>

    <!-- Content -->
    <ion-content :fullscreen="true" class="ion-padding" :style="{ '--background': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)' }">
      <div class="pb-20">
        <!-- Error Alert -->
        <div v-if="error" class="mb-4 p-4 rounded-lg bg-red-100 border-l-4 border-red-500">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center items-center" style="height: 300px;">
          <ion-spinner name="crescent" color="primary"></ion-spinner>
        </div>

        <!-- Waybill Details -->
        <div v-else-if="waybill" class="space-y-4">
          <!-- Header Card -->
          <div class="p-4 rounded-xl shadow-md" :style="{ backgroundColor: '#ffffff', borderLeft: `4px solid ${palette.primary}` }">
            <h2 class="text-lg font-bold mb-3" :style="{ color: palette.dark }">
              {{ waybill.number ? `Путевой лист №${waybill.number}` : 'Путевой лист' }}
            </h2>

            <!-- Key Info -->
            <div class="space-y-2 text-sm">
              <div>
                <p class="text-xs font-medium" :style="{ color: palette.medium }">Дата</p>
                <p class="font-semibold" :style="{ color: palette.dark }">{{ formatDate(waybill.date) }}</p>
              </div>

              <div>
                <p class="text-xs font-medium" :style="{ color: palette.medium }">Машина</p>
                <p class="font-semibold" :style="{ color: palette.dark }">
                  {{ waybill.car_brand && waybill.car_model ? `${waybill.car_brand} ${waybill.car_model}` : (waybill.car_name || 'Машина') }}
                </p>
                <p class="text-xs" :style="{ color: palette.medium }">{{ waybill.car_number || 'Без номера' }}</p>
              </div>

              <div v-if="waybill.status">
                <p class="text-xs font-medium" :style="{ color: palette.medium }">Статус</p>
                <p class="font-semibold" :style="{ color: getStatusColor() }">{{ getStatusLabel() }}</p>
              </div>
            </div>
          </div>

          <!-- Action Button -->
          <button
            @click="goToStartTrip"
            class="w-full px-4 py-3 rounded-lg font-semibold text-white transition-colors"
            :style="{
              backgroundColor: palette.primary,
              cursor: 'pointer',
            }"
          >
            ← Вернуться к началу поездки
          </button>
        </div>

        <!-- Empty State -->
        <div v-else class="flex flex-col items-center justify-center h-96 px-6">
          <ion-icon name="document-outline" style="font-size: 64px; color: #ccc; margin-bottom: 16px;"></ion-icon>
          <p class="text-gray-500 text-center w-full">Путевой лист не найден</p>
        </div>
      </div>
    </ion-content>

    <!-- Footer Navigation -->
    <footer-navigation />
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { waybillApi } from '../api'
import { palette } from '../components/ui/theme'
import { useAuthStore } from '../stores/auth'
import FooterNavigation from '../components/FooterNavigation.vue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonIcon,
  IonSpinner,
} from '@ionic/vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const waybillId = route.params.id
const waybill = ref(null)
const isLoading = ref(false)
const error = ref('')

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function getStatusColor() {
  if (!waybill.value) return palette.medium
  if (waybill.value.deleted_at) return palette.error
  return palette.success
}

function getStatusLabel() {
  if (!waybill.value) return 'Неизвестно'
  if (waybill.value.deleted_at) return 'Удален'
  return 'Активен'
}

function goBack() {
  router.back()
}

function goToStartTrip() {
  router.push(`/waybill/${waybillId}/start`)
}

async function loadWaybill() {
  isLoading.value = true
  error.value = ''

  try {
    if (!authStore.user || !authStore.user.id) {
      error.value = 'Пожалуйста, авторизуйтесь'
      return
    }

    const response = await waybillApi.list({ driver: authStore.user.id, include_car: 'true' })
    const data = response.data || []
    const foundWaybill = data.find(w => w.id === parseInt(waybillId))
    
    if (foundWaybill) {
      waybill.value = foundWaybill
      console.log('Waybill loaded:', waybill.value)
    } else {
      error.value = 'Путевой лист не найден'
    }
  } catch (err) {
    error.value = err.message || 'Ошибка загрузки путевого листа'
    console.error('Error loading waybill:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (waybillId) {
    loadWaybill()
  }
})
</script>

<style scoped>
.page-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.page-layout ion-content {
  flex: 1;
  overflow: auto;
}
</style>
