export interface CurrencyRateResponse {
  base: string;
  target: string;
  rate: number | string;
  last_updated: string;
}

export interface CurrencyConvertResponse {
  base: string;
  target: string;
  amount: number | string;
  converted_amount: number | string;
  rate: number | string;
  last_updated: string;
}
