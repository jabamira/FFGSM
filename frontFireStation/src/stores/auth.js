import { defineStore } from "pinia";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    access: null,
    serverError: false,
    lastVerifyTime: 0,
    lastVerifyResult: false,
    checkedOnce: false,
    healthIntervalId: null,
    permissions: {},
    permissionsLoaded: false,
    crudPermissions: {
      canCreate: false,
      canDelete: false,
    },
  }),

  getters: {
    isAuthenticated(state) {
      return !!state.access;
    },
  },

  actions: {
    setAccess(token) {
      this.access = token;

      if (token) {
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        localStorage.setItem("access", token);
      } else {
        delete axios.defaults.headers.common["Authorization"];
        localStorage.removeItem("access");
      }
    },

    setUser(user) {
      this.user = user;

      if (user) {
        try {
          localStorage.setItem("user", JSON.stringify(user));
        } catch (e) {
          console.error("[AUTH] Failed to save user to localStorage:", e);
        }
      } else {
        localStorage.removeItem("user");
      }
    },

    setPermissions(permissions) {
      if (permissions === null) {
        this.permissions = {};
        this.permissionsLoaded = false;
        return;
      }

      this.permissions = permissions || {};
      this.permissionsLoaded = true; // отметить что разрешения загружены

      if (permissions && Object.keys(permissions).length > 0) {
        try {
          localStorage.setItem("permissions", JSON.stringify(permissions));
          console.debug("[AUTH] Permissions saved to localStorage");
        } catch (e) {
          console.error(
            "[AUTH] Failed to save permissions to localStorage:",
            e,
          );
        }
      }
    },

    async login(login, password) {
      try {
        const res = await axios.post(`/auth/login/`, {
          login,
          password,
          client: "web",
        });

        const { access, user } = res.data;

        if (!access) return false;

        this.setAccess(access);
        this.setUser(user);

        this.checkedOnce = true;

        const permissionsLoaded = await this.fetchPermissionsWithRetry(3, 5000);
        if (!permissionsLoaded) {
          console.error(
            "[AUTH STORE] Failed to load permissions after login, cannot proceed",
          );
          // Откатываем state обратно потому что не смогли загрузить разрешения
          this.setAccess(null);
          this.setUser(null);
          this.setPermissions(null);
          return false;
        }

        console.log("[AUTH STORE] Permissions loaded successfully");
        this.startHealthPolling();
        console.log("[AUTH STORE] Login successful, redirecting to app");
        return true;
      } catch (err) {
        console.error(
          "[AUTH STORE] Login error:",
          err.response?.data || err.message,
        );
        this.checkedOnce = false;
        return false;
      }
    },

    async fetchPermissionsWithRetry(maxRetries = 3, timeout = 10000) {
      let lastError = null;

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          console.log(
            `[AUTH] Attempting to load permissions (attempt ${attempt}/${maxRetries})`,
          );

          // Используем Promise.race с timeout
          const permissionsLoaded = await Promise.race([
            this.fetchPermissions(),
            new Promise((_, reject) =>
              setTimeout(
                () => reject(new Error("Permission loading timeout")),
                timeout,
              ),
            ),
          ]);

          if (this.permissionsLoaded) {
            console.log("[AUTH] Permissions loaded successfully");
            return true;
          }
        } catch (error) {
          lastError = error;
          console.warn(
            `[AUTH] Attempt ${attempt} failed:`,
            error?.response?.data || error.message,
          );

          if (attempt < maxRetries) {
            const delay = 500 * Math.pow(2, attempt - 1);
            console.log(`[AUTH] Retrying after ${delay}ms...`);
            await new Promise((resolve) => setTimeout(resolve, delay));
          }
        }
      }

      console.error(
        "[AUTH] All permission loading attempts failed:",
        lastError?.message,
      );
      return false;
    },

    async fetchPermissions() {
      if (!this.user) {
        console.error("[AUTH] user missing");
        throw new Error("User not set");
      }

      try {
        const res = await axios.get(`/permissions/current/`, {
          headers: {
            Authorization: `Bearer ${this.access}`,
          },
        });

        this.setPermissions(res.data);
        console.debug("[AUTH] permissions loaded", this.permissions);
        return true;
      } catch (error) {
        console.error("[AUTH] permissions error", error);
        throw error;
      }
    },

    logout() {
      this.setAccess(null);
      this.setUser(null);
      this.setPermissions(null);
      this.permissionsLoaded = false;
      this.clearCrudPermissions();
      this.stopHealthPolling();
      localStorage.removeItem("access");
      localStorage.removeItem("user");
      localStorage.removeItem("permissions");
      console.log(
        "[AUTH] Logged out, cleared all data, permissionsLoaded:",
        this.permissionsLoaded,
      );
    },

    /**
     * Установить CRUD разрешения для текущей страницы
     */
    setCrudPermissions(crudPerms) {
      this.crudPermissions = {
        canCreate: crudPerms.canCreate || false,
        canDelete: crudPerms.canDelete || false,
      };
      console.debug("[AUTH] CRUD permissions updated:", this.crudPermissions);
    },

    /**
     * Очистить CRUD разрешения
     */
    clearCrudPermissions() {
      this.crudPermissions = {
        canCreate: false,
        canDelete: false,
      };
    },

    /**
     * Обновить отдельное CRUD разрешение
     */
    updateCrudPermission(permission, value) {
      if (this.crudPermissions.hasOwnProperty(permission)) {
        this.crudPermissions[permission] = value;
      }
    },

    loadFromStorage() {
      const token = localStorage.getItem("access");
      const storedUser = localStorage.getItem("user");
      const storedPermissions = localStorage.getItem("permissions");

      if (token) {
        this.setAccess(token);
      }

      if (storedUser) {
        try {
          this.user = JSON.parse(storedUser);
        } catch (e) {
          console.error("[AUTH] Failed to parse user from localStorage:", e);
          this.user = null;
        }
      }

      if (storedPermissions) {
        try {
          const parsed = JSON.parse(storedPermissions);
          this.setPermissions(parsed);
          console.log("[AUTH] Permissions restored from localStorage");
        } catch (e) {
          console.error(
            "[AUTH] Failed to parse permissions from localStorage:",
            e,
          );
          this.permissions = {};
          this.permissionsLoaded = false;
        }
      }

      if (this.access && this.user) {
        this.fetchPermissions().catch((err) => {
          console.warn(
            "[AUTH] Could not refresh permissions on startup, using cached",
          );
        });
        this.startHealthPolling();
      }
    },

    decodeToken() {
      try {
        const parts = this.access?.split(".");
        if (!parts || parts.length !== 3) return null;

        return JSON.parse(atob(parts[1]));
      } catch {
        return null;
      }
    },

    fetchUser() {
      if (!this.access) {
        this.logout();
        return null;
      }

      const payload = this.decodeToken();

      if (!payload || (payload.exp && payload.exp < Date.now() / 1000)) {
        this.logout();
        return null;
      }

      if (!this.user) {
        this.user = {
          id: payload.sub,
          login: payload.login,
          role: payload.role,
        };
      }

      return this.user;
    },

    async verify() {
      if (this.serverError) {
        this.lastVerifyResult = false;
        return false;
      }

      this.checkedOnce = true;

      let headerVal;

      if (this.access) {
        headerVal = `Bearer ${this.access}`;
        axios.defaults.headers.common["Authorization"] = headerVal;
      }

      try {
        const res = await axios.get(`/auth/me/`, {
          headers: headerVal ? { Authorization: headerVal } : {},
          timeout: 5000,
        });

        if (res.data && res.data.id) {
          this.setUser(res.data);
          return true;
        }
      } catch (err) {
        if (!err.response) {
          this.serverError = true;
          this.stopHealthPolling();
          return false;
        }

        if (err.response.status >= 500) {
          this.serverError = true;
          this.stopHealthPolling();
          return false;
        }

        if (err.response.status === 401 || err.response.status === 403) {
          if (this.access) {
            this.logout();
          }
          return false;
        }
      }

      return false;
    },

    clearServerError() {
      this.serverError = false;

      if (this.access) {
        this.startHealthPolling();
      }
    },

    async retryVerify() {
      this.clearServerError();
      this.lastVerifyTime = 0;
      this.checkedOnce = false;

      const ok = await this.verify();

      if (ok && this.access && !this.healthIntervalId) {
        this.startHealthPolling();
      }

      return ok;
    },

    startHealthPolling(intervalSeconds = 10) {
      if (this.healthIntervalId) return;

      this.healthIntervalId = setInterval(() => {
        this.checkConnection(intervalSeconds);
      }, intervalSeconds * 1000);
    },

    stopHealthPolling() {
      if (this.healthIntervalId) {
        clearInterval(this.healthIntervalId);
        this.healthIntervalId = null;
      }
    },

    async checkConnection(intervalSeconds = 10) {
      const now = Date.now();

      if (
        this.lastVerifyTime &&
        now - this.lastVerifyTime < intervalSeconds * 1000
      ) {
        return this.lastVerifyResult;
      }

      const ok = await this.verify();

      this.lastVerifyTime = Date.now();
      this.lastVerifyResult = ok;
      this.checkedOnce = true;

      return ok;
    },

    setupAxiosInterceptors() {
      axios.interceptors.request.use(
        (config) => {
          if (this.access) {
            config.headers = config.headers || {};
            config.headers.Authorization = `Bearer ${this.access}`;
          }

          return config;
        },
        (err) => Promise.reject(err),
      );

      axios.interceptors.response.use(
        (response) => response,
        (error) => {
          if (!error.response) {
            this.serverError = true;
            window.location.hash = "#/server-error";
            return Promise.reject(error);
          }

          const status = error.response.status;

          if (status >= 500) {
            this.serverError = true;
            window.location.hash = "#/server-error";
            return Promise.reject(error);
          }

          if (status === 401 || status === 403) {
            this.logout();
            window.location.hash = "#/auth";
          }

          return Promise.reject(error);
        },
      );
    },

    canAccessReports() {
      return !!(
        this.permissions.view_drivers_reports ||
        this.permissions.view_passenger_cars_reports ||
        this.permissions.view_fire_truck_reports
      );
    },

    getDefaultRedirectPath() {
      // Проверим, есть ли доступ к отчетам
      if (this.canAccessReports()) {
        return "/fuel-report";
      }

      if (this.permissions.view_users) {
        return "/users";
      }

      return "/";
    },
    isDriver() {
      if (this.user?.role) {
        const roleName =
          typeof this.user.role === "string"
            ? this.user.role
            : this.user.role?.name || this.user.role?.toString?.() || "";

        if (roleName.toLowerCase?.() === "водитель") {
          return true;
        }
      }

      if (
        this.permissionsLoaded &&
        !this.canAccessReports() &&
        !this.permissions.view_users &&
        !this.permissions.view_roles
      ) {
        return true;
      }

      return false;
    },
  },
});
