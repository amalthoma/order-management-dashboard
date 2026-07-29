import { OrderResponse } from './order';

export interface DashboardSummaryResponse {
  total_orders: number;
  pending_orders: number;
  processing_orders: number;
  completed_orders: number;
  cancelled_orders: number;
  total_revenue: number | string;
}

export interface StatusDistributionResponse {
  PENDING: number;
  PROCESSING: number;
  COMPLETED: number;
  CANCELLED: number;
}

export interface MonthlyStatisticItem {
  month: string;
  orders: number;
  revenue: number | string;
}

export interface MonthlyStatisticsResponse {
  items: MonthlyStatisticItem[];
}

export interface DashboardFullResponse {
  summary: DashboardSummaryResponse;
  recent_orders: OrderResponse[];
  status_distribution: StatusDistributionResponse;
  monthly_statistics: MonthlyStatisticsResponse;
}
