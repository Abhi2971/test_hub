import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.request.use(
  (config) => {
    if (config.url?.includes('/auth/refresh')) return config;
    const token = localStorage.getItem('auth_access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest.url.includes('/auth/refresh')) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;
      const refreshToken = localStorage.getItem('auth_refresh_token');

      if (!refreshToken) {
        clearAuthTokens();
        window.location = '/login';
        return Promise.reject(error);
      }

      try {
        const response = await api.post(
          '/auth/refresh',
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          }
        );

        const { access_token, refresh_token } = response.data.data;
        setAuthTokens(access_token, refresh_token);
        processQueue(null, access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearAuthTokens();
        window.location = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (error.response?.status === 402) {
      const event = new CustomEvent('subscription:required', {
        detail: error.response.data,
      });
      window.dispatchEvent(event);
    }

    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      const event = new CustomEvent('ratelimit:hit', {
        detail: { retryAfter, ...error.response.data },
      });
      window.dispatchEvent(event);
    }

    return Promise.reject(error);
  }
);

export const setAuthTokens = (accessToken, refreshToken) => {
  localStorage.setItem('auth_access_token', accessToken);
  localStorage.setItem('auth_refresh_token', refreshToken);
};

export const clearAuthTokens = () => {
  localStorage.removeItem('auth_access_token');
  localStorage.removeItem('auth_refresh_token');
};

export const getAccessToken = () => {
  return localStorage.getItem('auth_access_token');
};

export default api;
