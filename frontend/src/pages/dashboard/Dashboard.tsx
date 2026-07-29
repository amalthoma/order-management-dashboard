import React from 'react';
import { useDashboard } from '../../hooks/useDashboard';
import { useWebSocket } from '../../hooks/useWebSocket';
import { DashboardCard } from '../../components/charts/DashboardCard';
import { StatusPieChart } from '../../components/charts/StatusPieChart';
import { RevenueBarChart } from '../../components/charts/RevenueBarChart';
import { RecentOrdersTable } from '../../components/tables/RecentOrdersTable';
import { CurrencyWidget } from '../../components/charts/CurrencyWidget';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorState } from '../../components/common/ErrorState';
import { PageHeader } from '../../components/common/PageHeader';
import { ShoppingCart, Clock, CheckCircle2, DollarSign } from 'lucide-react';

export const Dashboard = () => {
  const { data: dashboardResp, isLoading, error, refetch } = useDashboard(10);
  useWebSocket();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorState message="Failed to load dashboard data." onRetry={refetch as any} />;
  
  const payload = dashboardResp?.data;
  if (!payload) {
    return (
      <div className="bg-blue-50 text-blue-700 p-4 rounded-lg border border-blue-100">
        No dashboard data available.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard Overview" />
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard 
          title="Total Orders" 
          value={payload.summary.total_orders} 
          icon={<ShoppingCart className="w-8 h-8 text-blue-600" />} 
          iconBg="bg-blue-100"
        />
        <DashboardCard 
          title="Pending" 
          value={payload.summary.pending_orders} 
          icon={<Clock className="w-8 h-8 text-yellow-600" />} 
          iconBg="bg-yellow-100"
        />
        <DashboardCard 
          title="Completed" 
          value={payload.summary.completed_orders} 
          icon={<CheckCircle2 className="w-8 h-8 text-green-600" />} 
          iconBg="bg-green-100"
        />
        <DashboardCard 
          title="Revenue" 
          value={`$${Number(payload.summary.total_revenue).toFixed(2)}`} 
          icon={<DollarSign className="w-8 h-8 text-purple-600" />} 
          iconBg="bg-purple-100"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RevenueBarChart data={payload.monthly_statistics.items} />
        </div>
        <div className="lg:col-span-1">
          <StatusPieChart data={payload.status_distribution} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentOrdersTable orders={payload.recent_orders} />
        </div>
        <div className="lg:col-span-1">
          <CurrencyWidget />
        </div>
      </div>
    </div>
  );
};
