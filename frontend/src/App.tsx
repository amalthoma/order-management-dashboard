import React from 'react';
import { BrowserRouter } from 'react-router';
import { AppProviders } from './providers/AppProviders';
import { AppRoutes } from './routes';

export const App = () => {
  return (
    <AppProviders>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AppProviders>
  );
};
