import React from 'react';
import { cn } from '../../utils/utils';

export const StatusBadge = ({ status }: { status: string }) => {
  const getStyles = () => {
    switch (status.toLowerCase()) {
      case 'completed': return 'bg-green-100 text-green-700 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'cancelled': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-semibold border", getStyles())}>
      {status.charAt(0).toUpperCase() + status.slice(1).toLowerCase()}
    </span>
  );
};
