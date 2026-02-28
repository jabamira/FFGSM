import { createRouter, createWebHashHistory } from "vue-router";
import Auth from "../views/Auth.vue";
import FuelReport from "../views/FuelReport.vue";
import UIComponentsPage from "../views/UIComponentsPage.vue";
import ServerError from "../views/ServerError.vue";
import { useAuthStore } from "../stores/auth"; // used in navigation guard

const routes = [
  // root path redirects depending on auth state (guard will handle afterwards)
  { path: "/", redirect: "/auth" },
  { path: "/auth", component: Auth },
  { path: "/fuel-report", component: FuelReport, meta: { requiresAuth: true } },
  {
    path: "/ui-elements",
    component: UIComponentsPage,
    meta: { requiresAuth: true },
  },
  { path: "/server-error", component: ServerError }, // catch all and send back to auth (could be 404 page)
  { path: "/:catchAll(.*)", redirect: "/" },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// global navigation guard (non-blocking for subsequent checks)
router.beforeEach(async (to) => {
  const auth = useAuthStore();

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
  }

  if (to.path === "/auth" && auth.isAuthenticated) {
    return "/fuel-report";
  }
});

export default router;
