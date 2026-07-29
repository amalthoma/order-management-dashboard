export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface StandardResponse<T> {
  success: boolean;
  data: T;
  message: string;
  error: string | null;
}
