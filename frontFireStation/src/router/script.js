import { createRouter, createWebHashHistory } from "vue-router";
import Auth from "../views/Auth.vue";
import FuelReport from "../views/FuelReport.vue";
import UIComponentsPage from "../views/UIComponentsPage.vue";
import ServerError from "../views/ServerError.vue";
import Drivers from "../views/Drivers.vue";
import Users from "../views/Users.vue";
import FireTrucksList from "../views/FireTrucksList.vue";
import FireTrucksWayBills from "../views/FireTrucksWayBills.vue";
import FireTrucksNorms from "../views/FireTrucksNorms.vue";
import LightVehiclesList from "../views/LightVehiclesList.vue";
import LightVehiclesWayBills from "../views/LightVehiclesWayBills.vue";
import LightVehiclesNorms from "../views/LightVehiclesNorms.vue";
import WaybillManagement from "../views/WaybillManagement.vue";
import { useAuthStore } from "../stores/auth"; // used in navigation guard

const routes = [
  // root path redirects depending on auth state (guard will handle afterwards)
  { path: "/", redirect: "/auth" },
  { path: "/auth", component: Auth },
  { path: "/fuel-report", component: FuelReport, meta: { requiresAuth: true } },
  { path: "/drivers", component: Drivers, meta: { requiresAuth: true } },
  { path: "/users", component: Users, meta: { requiresAuth: true } },
  {
    path: "/roles",
    component: () => import("../views/Roles.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/fire-trucks-list",
    component: FireTrucksList,
    meta: { requiresAuth: true },
  },
  {
    path: "/fire-trucks-waybills",
    component: FireTrucksWayBills,
    meta: { requiresAuth: true },
  },
  {
    path: "/fire-truck-waybill/:id",
    component: WaybillManagement,
    meta: { requiresAuth: true },
  },
  {
    path: "/fire-trucks-norms",
    component: FireTrucksNorms,
    meta: { requiresAuth: true },
  },
  {
    path: "/light-vehicles-list",
    component: LightVehiclesList,
    meta: { requiresAuth: true },
  },
  {
    path: "/light-vehicles-waybills",
    component: LightVehiclesWayBills,
    meta: { requiresAuth: true },
  },
  {
    path: "/passenger-car-waybill/:id",
    component: WaybillManagement,
    meta: { requiresAuth: true },
  },
  {
    path: "/light-vehicles-norms",
    component: LightVehiclesNorms,
    meta: { requiresAuth: true },
  },
  {
    path: "/ui-elements",
    component: UIComponentsPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/server-error",
    component: ServerError,
    // if we somehow land here but the server is healthy, bounce to auth/root
    beforeEnter: async (to, from) => {
      const auth = useAuthStore();
      const ok = await auth.checkConnection();
      if (ok) {
        // clear the flag so navigation guard won't redirect us back
        auth.clearServerError();
        // navigate to root which will redirect to /auth and then to /fuel-report if logged in
        return "/";
      }
      // otherwise stay on error page
      return true;
    },
  }, // catch all and send back to auth (could be 404 page)
  { path: "/:catchAll(.*)", redirect: "/" },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// global navigation guard (non-blocking for subsequent checks)
router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (to.path !== "/server-error") {
    await auth.checkConnection();
    // only redirect if the store believes the server is actually down.
    if (auth.serverError) {
      return "/server-error";
    }
  }

  // if server previously failed, go straight to error page (unless we are already there)
  if (auth.serverError && to.path !== "/server-error") {
    return "/server-error";
  }

  if (to.meta.requiresAuth) {
    if (!auth.isAuthenticated) {
      return "/auth";
    }

    // if we haven't ever checked before, block until result
    if (!auth.checkedOnce) {
      const ok = await auth.checkConnection();
      if (!ok) {
        return auth.serverError ? "/server-error" : "/auth";
      }
    } else {
      // start a background check but don't wait for it to finish
      auth.checkConnection().then((ok) => {
        if (!ok) {
          if (auth.serverError) {
            router.replace("/server-error");
          } else {
            router.replace("/auth");
          }
        }
      });
    }

    // ВАЖНО: Убедиться, что разрешения загружены перед переходом на защищённую страницу
    // Если разрешения не загружены, синхронно дождаться их загрузки перед переходом
    // Это необходимо чтобы компоненты получили правильное состояние при монтировании
    if (!auth.permissionsLoaded) {
      console.log(
        "[ROUTER] Permissions not yet loaded, waiting for sync load before proceeding to protected route",
      );
      const permissionsLoaded = await auth.fetchPermissionsWithRetry(3, 10000);

      if (!permissionsLoaded) {
        console.warn(
          "[ROUTER] Failed to load permissions, allowing to proceed but with empty permissions",
        );
        // Всё равно разрешаем переход, но с пустыми разрешениями
        // Это позволяет пользователю видеть красивую ошибку вместо полного зависания
      }
    }
  }

  if (to.path === "/auth" && auth.isAuthenticated) {
    return "/fuel-report";
  }
});

export default router;
