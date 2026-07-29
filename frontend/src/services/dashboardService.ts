import { apiClient } from '../lib/axios';
import { ENDPOINTS } from '../api/endpoints';
import { StandardResponse } from '../types/auth';
import { DashboardFullResponse } from '../types/dashboard';

export const dashboardService = {
  getDashboard: async (limit: number = 10): Promise<StandardResponse<DashboardFullResponse>> => {
    const response = await apiClient.get<StandardResponse<DashboardFullResponse>>(ENDPOINTS.DASHBOARD.BASE, {
      params: { limit },
    });
    return response.data;
  },
};
