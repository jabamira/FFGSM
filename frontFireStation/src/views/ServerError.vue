<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
    <div class="w-full max-w-md bg-white rounded-lg shadow p-8" :style="{ borderColor: palette.light }">
      <div class="text-center space-y-6">
        <h1 class="text-3xl font-bold mb-4" :style="{ color: palette.dark }">Ошибка соединения</h1>
        <p class="text-lg" :style="{ color: palette.dark }">Сервер не отвечает. Пожалуйста, попробуйте позже.</p>
        <Button :loading="loading" variant="primary" @click="onRetry">{{ buttonLabel }}</Button>
        <p v-if="message" class="text-sm" :style="{ color: palette.error }">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import Button from "../components/ui/Button.vue";
import { palette } from '../components/ui/importUi';
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const loading = ref(false);
const message = ref('');
const buttonLabel = ref('Повторить');

async function onRetry() {
  if (loading.value) return false;
  loading.value = true;
  message.value = '';
  const ok = await auth.retryVerify();
  if (ok) {
    router.push("/");
    return true;
  } else {
    // keep error page, show message, allow try again after timeout
    message.value = 'Пока не удалось связаться, попробуйте ещё раз.';
    buttonLabel.value = 'Ещё раз';
    // ensure we don't spam verify immediately by waiting interval
    setTimeout(() => {
      loading.value = false;
    }, 10000); // 10s cooldown before allowing next retry
    return false;
  }
}

// when this component loads, try immediately and keep polling until success
let pollId = null;

onMounted(() => {
  attemptOnceAndPoll();
});

onBeforeUnmount(() => {
  if (pollId) {
    clearInterval(pollId);
    pollId = null;
  }
});

async function attemptOnceAndPoll() {
  const success = await onRetry();
  if (!success && !pollId) {
    pollId = setInterval(async () => {
      const again = await onRetry();
      if (again) {
        clearInterval(pollId);
        pollId = null;
      }
    }, 3000);
  }
}
</script>

<style scoped>
</style>
