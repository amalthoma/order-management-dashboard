import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useUpdateOrderStatus } from '../../hooks/useOrders';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import toast from 'react-hot-toast';

const UpdateStatusSchema = z.object({
  status: z.enum(['PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED']),
});

type UpdateStatusData = z.infer<typeof UpdateStatusSchema>;

interface Props {
  isOpen: boolean;
  onClose: () => void;
  orderId: string;
  currentStatus: string;
}

export const UpdateStatusDialog = ({ isOpen, onClose, orderId, currentStatus }: Props) => {
  const updateStatus = useUpdateOrderStatus();
  
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<UpdateStatusData>({
    resolver: zodResolver(UpdateStatusSchema),
    defaultValues: { status: currentStatus as any },
  });

  const onSubmit = async (data: UpdateStatusData) => {
    if (data.status === currentStatus) {
      onClose();
      return;
    }
    try {
      await updateStatus.mutateAsync({ id: orderId, data: { status: data.status as any } });
      toast.success('Order status updated!');
      onClose();
    } catch (err: any) {
      toast.error('Failed to update status');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Update Order #${orderId}`}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">New Status</label>
          <select
            {...register('status')}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md transition-colors border"
          >
            <option value="PENDING">Pending</option>
            <option value="PROCESSING">Processing</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100 mt-6">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            Update Status
          </Button>
        </div>
      </form>
    </Modal>
  );
};
