import { z } from 'zod';

export const currencyConvertSchema = z.object({
  base: z.string().length(3, 'Must be exactly 3 characters').toUpperCase(),
  target: z.string().length(3, 'Must be exactly 3 characters').toUpperCase(),
  amount: z.coerce.number().positive('Amount must be positive'),
});

export type CurrencyConvertData = z.infer<typeof currencyConvertSchema>;
