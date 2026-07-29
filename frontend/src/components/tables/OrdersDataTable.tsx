import React, { useState } from 'react';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { OrderResponse } from '../../types/order';
import { StatusBadge } from '../common/StatusBadge';
import { UpdateStatusDialog } from '../forms/UpdateStatusDialog';
import { ChevronUp, ChevronDown, Edit } from 'lucide-react';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface Props {
  data: OrderResponse[];
  total: number;
  page: number;
  limit: number;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onSort: (field: string, desc: boolean) => void;
  sortBy?: string;
  sortDesc?: boolean;
}

const columnHelper = createColumnHelper<OrderResponse>();

export const OrdersDataTable = ({ data, total, page, limit, isLoading, onPageChange, onSort, sortBy, sortDesc }: Props) => {
  const [editingOrder, setEditingOrder] = useState<OrderResponse | null>(null);

  const columns = [
    columnHelper.accessor('id', {
      header: 'ID',
      cell: (info) => <span className="text-gray-500">#{info.getValue()}</span>,
    }),
    columnHelper.accessor('customer_name', {
      header: 'Customer',
      cell: (info) => <span className="font-medium text-gray-900">{info.getValue()}</span>,
    }),
    columnHelper.accessor('amount', {
      header: 'Amount',
      cell: (info) => `$${Number(info.getValue()).toFixed(2)}`,
    }),
    columnHelper.accessor('status', {
      header: 'Status',
      cell: (info) => <StatusBadge status={info.getValue()} />,
    }),
    columnHelper.accessor('created_at', {
      header: 'Date',
      cell: (info) => new Date(info.getValue()).toLocaleDateString(),
    }),
    columnHelper.display({
      id: 'actions',
      header: 'Actions',
      cell: (info) => (
        <button
          onClick={() => setEditingOrder(info.row.original)}
          className="p-1 text-gray-400 hover:text-blue-600 transition-colors rounded hover:bg-blue-50"
          title="Update Status"
        >
          <Edit size={18} />
        </button>
      ),
    }),
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    manualSorting: true,
  });

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="w-full flex flex-col">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-600">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-700">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th 
                    key={header.id} 
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-gray-100 transition-colors select-none"
                    onClick={() => {
                      if (header.id === 'actions') return;
                      const isDesc = sortBy === header.id ? !sortDesc : false;
                      onSort(header.id, isDesc);
                    }}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                      {sortBy === header.id && (
                        sortDesc ? <ChevronDown size={14} /> : <ChevronUp size={14} />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {isLoading ? (
              <tr>
                <td colSpan={columns.length} className="h-64 text-center">
                  <LoadingSpinner fullScreen={false} />
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="h-32 text-center text-gray-500">
                  No orders found.
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-6 py-4 whitespace-nowrap">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between px-6 py-3 border-t border-gray-200 bg-gray-50">
        <div className="text-sm text-gray-500">
          Showing <span className="font-medium">{(page - 1) * limit + (data.length > 0 ? 1 : 0)}</span> to <span className="font-medium">{(page - 1) * limit + data.length}</span> of <span className="font-medium">{total}</span> results
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1 || isLoading}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages || isLoading}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>

      {editingOrder && (
        <UpdateStatusDialog
          isOpen={!!editingOrder}
          onClose={() => setEditingOrder(null)}
          orderId={editingOrder.id}
          currentStatus={editingOrder.status}
        />
      )}
    </div>
  );
};
