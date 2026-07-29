import { apiClient } from '../lib/axios';
import { ENDPOINTS } from '../api/endpoints';
import { StandardResponse } from '../types/auth';
import { OrderResponse, PaginatedResponse } from '../types/order';
import { OrderCreateData, OrderFilterData, OrderUpdateStatusData } from '../schemas/orderSchema';

export const orderService = {
  listOrders: async (filters: OrderFilterData): Promise<StandardResponse<PaginatedResponse<OrderResponse>>> => {
    const response = await apiClient.get<StandardResponse<PaginatedResponse<OrderResponse>>>(ENDPOINTS.ORDERS.BASE, {
      params: filters,
    });
    return response.data;
  },
  
  createOrder: async (data: OrderCreateData): Promise<StandardResponse<OrderResponse>> => {
    const response = await apiClient.post<StandardResponse<OrderResponse>>(ENDPOINTS.ORDERS.BASE, data);
    return response.data;
  },

  getOrder: async (id: string): Promise<StandardResponse<OrderResponse>> => {
    const response = await apiClient.get<StandardResponse<OrderResponse>>(`${ENDPOINTS.ORDERS.BASE}/${id}`);
    return response.data;
  },

  updateStatus: async (id: string, data: OrderUpdateStatusData): Promise<StandardResponse<OrderResponse>> => {
    const response = await apiClient.patch<StandardResponse<OrderResponse>>(`${ENDPOINTS.ORDERS.BASE}/${id}/status`, data);
    return response.data;
  },
};
