import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import { createPinia } from "pinia";
import router from "./router/script";

const app = createApp(App);

// configure global axios defaults
import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api"; // matches backend
axios.defaults.baseURL = API_URL;
// tokens are handled manually, no cookies

const pinia = createPinia();
app.use(pinia); // сначала Pinia
app.use(router); // потом router

// restore auth state from localStorage
import { useAuthStore } from "./stores/auth";
const auth = useAuthStore(pinia);
auth.loadFromStorage();
auth.fetchUser(); // local expiration check
// set up interceptors before making any server calls
auth.setupAxiosInterceptors(); // catch 401 errors and attach token

// if serverError flag toggles anywhere, make sure we land on the error view
import { watch } from "vue";
watch(
  () => auth.serverError,
  (val) => {
    if (val && router.currentRoute.value.path !== "/server-error") {
      router.replace("/server-error");
    }
  },
);

// verify with server to catch password change or invalidation
// fire in background, don't block UI
auth.checkConnection().then((ok) => {
  if (!ok) {
    router.push("/server-error");
  }
});

app.mount("#app");
