
import axios from 'axios';
import type { Product, Market, PriceComparison } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Products
export const searchProducts = async (query: string, limit = 10): Promise<Product[]> => {
  const response = await api.get(`/api/v1/products/search`, {
    params: { q: query, limit },
  });
  return response.data;
};

export const getProduct = async (productId: string): Promise<Product> => {
  const response = await api.get(`/api/v1/products/${productId}`);
  return response.data;
};

// Markets
export const getNearbyMarkets = async (
  lat: number,
  lng: number,
  radius = 10
): Promise<Market[]> => {
  const response = await api.get(`/api/v1/markets/nearby`, {
    params: { lat, lng, radius },
  });
  return response.data;
};

export const getMarket = async (marketId: string): Promise<Market> => {
  const response = await api.get(`/api/v1/markets/${marketId}`);
  return response.data;
};

// Prices
export const getPriceComparison = async (
  productId: string,
  lat: number,
  lng: number,
  radius = 10
): Promise<PriceComparison> => {
  const response = await api.get(`/api/v1/prices/product/${productId}`, {
    params: { lat, lng, radius },
  });
  return response.data;
};

export const getPricesByMarket = async (
  marketId: string,
  limit = 50
): Promise<any> => {
  const response = await api.get(`/api/v1/prices/market/${marketId}`, {
    params: { limit },
  });
  return response.data;
};

// Auth
export const login = async (email: string, password: string) => {
  const response = await api.post(`/api/v1/auth/login`, { email, password });
  return response.data;
};

export const register = async (email: string, password: string, name: string) => {
  const response = await api.post(`/api/v1/auth/register`, { email, password, name });
  return response.data;
};

export default api;
