import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { orderCreateSchema, OrderCreateData } from '../../schemas/orderSchema';
import { useCreateOrder } from '../../hooks/useOrders';
import { Modal } from '../common/Modal';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import toast from 'react-hot-toast';
import { AlertCircle } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const OrderForm = ({ isOpen, onClose, onSuccess }: Props) => {
  const createOrder = useCreateOrder();
  
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<OrderCreateData>({
    resolver: zodResolver(orderCreateSchema),
  });

  const onSubmit = async (data: OrderCreateData) => {
    try {
      await createOrder.mutateAsync(data);
      toast.success('Order created successfully!');
      reset();
      onSuccess?.();
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || 'Failed to create order');
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Create New Order">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {createOrder.isError && (
          <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm flex items-start gap-2 border border-red-100">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{(createOrder.error as any)?.response?.data?.error?.message || 'An error occurred'}</span>
          </div>
        )}
        
        <Input
          label="Customer Name"
          type="text"
          placeholder="John Doe"
          {...register('customer_name')}
          error={errors.customer_name?.message}
        />
        
        <Input
          label="Amount"
          type="number"
          step="0.01"
          placeholder="0.00"
          {...register('amount', { valueAsNumber: true })}
          error={errors.amount?.message}
        />

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100 mt-6">
          <Button type="button" variant="ghost" onClick={handleClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            Create Order
          </Button>
        </div>
      </form>
    </Modal>
  );
};
