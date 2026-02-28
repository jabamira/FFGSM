import { defineStore } from "pinia";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    access: null,
    serverError: false, // true when network/server not responding
    lastVerifyTime: 0, // timestamp when verify was last performed
    lastVerifyResult: false,
    checkedOnce: false, // whether we've ever performed a connection check
    healthIntervalId: null, // id for periodic /auth/me polling
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
        localStorage.setItem("user", JSON.stringify(user));
      } else {
        localStorage.removeItem("user");
      }
    },

    async login(login, password) {
      try {
        // axios.baseURL already set to API_URL, so just use relative path
        const res = await axios.post(`/auth/login/`, {
          login,
          password,
          client: "web",
        });

        const { access, user } = res.data;
        console.debug("[AUTH] login response token", access);
        if (!access) {
          return false;
        }

        this.setAccess(access);
        this.setUser(user);
        this.startHealthPolling();
        return true;
      } catch (err) {
        console.error(
          "[AUTH STORE] Login error:",
          err.response?.data || err.message,
        );
        return false;
      }
    },

    logout() {
      this.setAccess(null);
      this.setUser(null);
      this.stopHealthPolling();
    },

    // restore token/user from localStorage on page load
    loadFromStorage() {
      // whenever we rehydrate we may want to resume health checks
      if (this.access) {
        this.startHealthPolling();
      }
      const token = localStorage.getItem("access");
      const storedUser = localStorage.getItem("user");

      if (token) {
        this.setAccess(token);
      }
      if (storedUser) {
        try {
          this.user = JSON.parse(storedUser);
        } catch (_) {
          this.user = null;
        }
      }
    },

    // decode token payload
    decodeToken() {
      try {
        const parts = this.access?.split(".");
        if (!parts || parts.length !== 3) return null;
        return JSON.parse(atob(parts[1]));
      } catch {
        return null;
      }
    },

    // ensure `user` field matches token; called by router guard
    fetchUser() {
      if (!this.access) {
        this.logout();
        return null;
      }
      const payload = this.decodeToken();
      if (!payload || (payload.exp && payload.exp < Date.now() / 1000)) {
        // expired or invalid token
        this.logout();
        return null;
      }
      // token contains user data as `sub`, `login`, `role`
      if (!this.user) {
        this.user = {
          id: payload.sub,
          login: payload.login,
          role: payload.role,
        };
      }
      return this.user;
    },

    // verify token by making real request to server (/api/auth/me)
    // returns true if valid, false otherwise; throws on network error
    async verify() {
      // clear cached result when serverError flips back
      if (this.serverError) {
        this.lastVerifyResult = false;
      }
      if (this.serverError) {
        // previously flagged as down, do not spam requests
        return false;
      }
      // mark that we've attempted verification even if early-return
      this.checkedOnce = true;
      if (!this.access) {
        this.logout();
        return false;
      }
      // ensure header is definitely set locally and then pass it explicitly
      const headerVal = `Bearer ${this.access}`;
      axios.defaults.headers.common["Authorization"] = headerVal;
      console.debug(
        "[AUTH] verify header explicit",
        headerVal,
        "access state",
        this.access,
      );
      try {
        const res = await axios.get(`/auth/me/`, {
          headers: { Authorization: headerVal },
          timeout: 5000, // fail quickly if server is unreachable
        });
        if (res.data && res.data.id) {
          // update user with returned data (in case server changed)
          this.setUser(res.data);
          return true;
        }
      } catch (err) {
        if (!err.response) {
          // no response => network/server down
          this.serverError = true;
          return false; // consume error
        }
        // treat server-side 5xx as 'down' as well
        if (err.response.status >= 500) {
          this.serverError = true;
          return false;
        }
        if (err.response.status === 401 || err.response.status === 403) {
          // token invalid, missing, or password changed
          this.logout();
          return false;
        }
      }
      return false;
    },

    clearServerError() {
      this.serverError = false;
    },

    async retryVerify() {
      this.clearServerError();
      // also reset timestamp so next call actually pings
      this.lastVerifyTime = 0;
      this.checkedOnce = false;
      return await this.verify();
    },

    // periodically poll /auth/me so we can detect downtime even when idle
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

    // throttled server check to avoid spamming /auth/me
    // returns cached result if called again within intervalSeconds
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

    // setup axios interceptor to catch 401 errors (invalid/expired token)
    setupAxiosInterceptors() {
      // request interceptor ensures token header is always attached (handles timing issues)
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
          // no response at all (network down, CORS failure, timeout)
          if (!error.response) {
            console.warn("[AUTH] network/server error", error.message);
            this.serverError = true;
            // fallback navigation to server error view
            window.location.hash = "#/server-error";
            return Promise.reject(error);
          }

          const status = error.response.status;
          // treat any 5xx as server down
          if (status >= 500) {
            console.warn("[AUTH] server error status", status);
            this.serverError = true;
            window.location.hash = "#/server-error";
            return Promise.reject(error);
          }

          // if server returns 401/403, token is invalid (password changed, user blocked, etc.)
          if (status === 401 || status === 403) {
            console.warn(
              "[AUTH] Server returned 401/403 - token is invalid or missing. Logging out.",
            );
            this.logout();
            // redirect to auth page
            window.location.hash = "#/auth";
          }
          return Promise.reject(error);
        },
      );
    },
  },
});
