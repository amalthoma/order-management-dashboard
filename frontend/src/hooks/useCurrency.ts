import { useQuery } from '@tanstack/react-query';
import { currencyService } from '../services/currencyService';

export const useCurrencyRate = (base: string, target: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['currencyRate', base, target],
    queryFn: () => currencyService.getRate(base, target),
    enabled: enabled && !!base && !!target,
  });
};

export const useCurrencyConvert = (base: string, target: string, amount: number, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['currencyConvert', base, target, amount],
    queryFn: () => currencyService.convert(base, target, amount),
    enabled: enabled && !!base && !!target && amount > 0,
  });
};
