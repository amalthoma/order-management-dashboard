import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { websocketService } from '../services/websocketService';

export const useWebSocket = () => {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();

    // Subscribe to events
    const unsubscribe = websocketService.subscribe((payload) => {
      if (payload.event === 'ORDER_STATUS_UPDATED') {
        // Invalidate queries to trigger a refetch
        queryClient.invalidateQueries({ queryKey: ['orders'] });
        queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      }
    });

    // Cleanup on unmount
    return () => {
      unsubscribe();
      websocketService.disconnect();
    };
  }, [queryClient]);
};
