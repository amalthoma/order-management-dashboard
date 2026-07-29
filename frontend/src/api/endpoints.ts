export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';

export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
  },
  ORDERS: {
    BASE: '/orders',
  },
  DASHBOARD: {
    BASE: '/dashboard',
  },
  CURRENCY: {
    RATE: '/currency/rate',
    CONVERT: '/currency/convert',
  },
};
