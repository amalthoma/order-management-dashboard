import { z } from 'zod';
import { OrderStatus } from '../types/order';

export const orderCreateSchema = z.object({
  customer_name: z.string().min(1, 'Customer name is required').max(150, 'Too long'),
  amount: z.coerce.number().positive('Amount must be greater than zero'),
});

export type OrderCreateData = z.infer<typeof orderCreateSchema>;

export const orderUpdateStatusSchema = z.object({
  status: z.nativeEnum(OrderStatus),
});

export type OrderUpdateStatusData = z.infer<typeof orderUpdateStatusSchema>;

export const orderFilterSchema = z.object({
  search: z.string().optional(),
  status: z.nativeEnum(OrderStatus).optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  sort_by: z.enum(['created_at', 'customer_name', 'amount', 'status']).default('created_at'),
  sort_order: z.enum(['asc', 'desc']).default('desc'),
  page: z.coerce.number().min(1).default(1),
  page_size: z.coerce.number().min(1).max(100).default(10),
});

export type OrderFilterData = z.infer<typeof orderFilterSchema>;
