import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';

export const useDashboard = (limit: number = 10) => {
  return useQuery({
    queryKey: ['dashboard', limit],
    queryFn: () => dashboardService.getDashboard(limit),
  });
};
