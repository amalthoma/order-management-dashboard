import { apiClient } from '../lib/axios';
import { ENDPOINTS } from '../api/endpoints';
import { LoginFormData } from '../schemas/loginSchema';
import { StandardResponse, TokenResponse } from '../types/auth';

export const authService = {
  login: async (credentials: LoginFormData): Promise<StandardResponse<TokenResponse>> => {
    const response = await apiClient.post<StandardResponse<TokenResponse>>(ENDPOINTS.AUTH.LOGIN, credentials);
    return response.data;
  },
};
