import { apiClient } from '../lib/axios';
import { ENDPOINTS } from '../api/endpoints';
import { StandardResponse } from '../types/auth';
import { CurrencyRateResponse, CurrencyConvertResponse } from '../types/currency';

export const currencyService = {
  getRate: async (base: string, target: string): Promise<StandardResponse<CurrencyRateResponse>> => {
    const response = await apiClient.get<StandardResponse<CurrencyRateResponse>>(ENDPOINTS.CURRENCY.RATE, {
      params: { base, target },
    });
    return response.data;
  },

  convert: async (base: string, target: string, amount: number): Promise<StandardResponse<CurrencyConvertResponse>> => {
    const response = await apiClient.get<StandardResponse<CurrencyConvertResponse>>(ENDPOINTS.CURRENCY.CONVERT, {
      params: { base, target, amount },
    });
    return response.data;
  }
};
