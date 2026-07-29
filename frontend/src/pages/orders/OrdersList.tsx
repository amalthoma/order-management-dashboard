import React, { useState } from 'react';
import { useOrders } from '../../hooks/useOrders';
import { OrdersDataTable } from '../../components/tables/OrdersDataTable';
import { OrderFilterToolbar } from '../../components/common/OrderFilterToolbar';
import { PageHeader } from '../../components/common/PageHeader';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { OrderForm } from '../../components/forms/OrderForm';
import { OrderFilterData } from '../../schemas/orderSchema';

export const OrdersList = () => {
  const [filters, setFilters] = useState<OrderFilterData>({
    page: 1,
    page_size: 10,
    status: undefined,
    search: undefined,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data: paginatedOrders, isLoading, refetch } = useOrders(filters);

  const handleFilterChange = (newFilters: Partial<OrderFilterData>) => {
    setFilters((prev: OrderFilterData) => ({ ...prev, ...newFilters, page: 1 }));
  };

  const handlePageChange = (newPage: number) => {
    setFilters((prev: OrderFilterData) => ({ ...prev, page: newPage }));
  };

  const handleSort = (field: string, desc: boolean) => {
    // Cast to expected sort_by types based on schema
    const validFields = ['created_at', 'customer_name', 'amount', 'status'];
    const sortField = validFields.includes(field) ? field as any : 'created_at';
    setFilters((prev: OrderFilterData) => ({ ...prev, sort_by: sortField, sort_order: desc ? 'desc' : 'asc' }));
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Orders" 
        action={
          <Button onClick={() => setIsCreateModalOpen(true)} className="flex items-center gap-2">
            <Plus size={18} />
            Create Order
          </Button>
        }
      />
      
      <OrderFilterToolbar filters={filters} onFilterChange={handleFilterChange} />
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <OrdersDataTable 
          data={paginatedOrders?.data.items || []}
          total={paginatedOrders?.data.pagination.total_records || 0}
          page={filters.page || 1}
          limit={filters.page_size || 10}
          isLoading={isLoading}
          onPageChange={handlePageChange}
          onSort={handleSort}
          sortBy={filters.sort_by}
          sortDesc={filters.sort_order === 'desc'}
        />
      </div>

      <OrderForm 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onSuccess={() => {
          setIsCreateModalOpen(false);
          refetch();
        }}
      />
    </div>
  );
};
