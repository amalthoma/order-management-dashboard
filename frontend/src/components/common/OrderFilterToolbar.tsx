import React from 'react';
import { OrderFilterData } from '../../schemas/orderSchema';
import { Search } from 'lucide-react';

interface Props {
  filters: OrderFilterData;
  onFilterChange: (filters: Partial<OrderFilterData>) => void;
}

export const OrderFilterToolbar = ({ filters, onFilterChange }: Props) => {
  return (
    <div className="flex flex-col sm:flex-row gap-4 p-4 bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="relative flex-1">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors"
          placeholder="Search by customer name..."
          value={filters.search || ''}
          onChange={(e) => onFilterChange({ search: e.target.value || undefined })}
        />
      </div>
      
      <div className="sm:w-48">
        <select
          className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md transition-colors"
          value={filters.status || ''}
          onChange={(e) => onFilterChange({ status: e.target.value as any || undefined })}
        >
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="PROCESSING">Processing</option>
          <option value="COMPLETED">Completed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>
    </div>
  );
};
