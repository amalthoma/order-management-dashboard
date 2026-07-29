import React, { useState } from 'react';
import { useCurrencyRate } from '../../hooks/useCurrency';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ArrowRightLeft, DollarSign } from 'lucide-react';

const CurrencyRow = ({ base, target }: { base: string, target: string }) => {
  const { data, isLoading, error } = useCurrencyRate(base, target);

  return (
    <li className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border border-gray-100">
      <div className="flex items-center gap-2 font-medium text-gray-700">
        <span>{base}</span>
        <ArrowRightLeft size={14} className="text-gray-400" />
        <span>{target}</span>
      </div>
      <div className="font-bold text-gray-900">
        {isLoading ? (
          <span className="text-gray-400 text-sm animate-pulse">Loading...</span>
        ) : error ? (
          <span className="text-red-500 text-sm">Error</span>
        ) : (
          Number(data?.data?.rate || 0).toFixed(4) || 'N/A'
        )}
      </div>
    </li>
  );
};

export const CurrencyWidget = () => {
  const [baseCurrency, setBaseCurrency] = useState('USD');
  const topCurrencies = ['EUR', 'GBP', 'JPY', 'INR', 'AED'];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <DollarSign className="text-green-600" size={20} />
          Exchange Rates
        </h3>
        <select 
          value={baseCurrency}
          onChange={(e) => setBaseCurrency(e.target.value)}
          className="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-1.5 bg-gray-50 outline-none border"
        >
          <option value="USD">USD</option>
          <option value="EUR">EUR</option>
          <option value="GBP">GBP</option>
        </select>
      </div>

      <div className="flex-1">
        <ul className="space-y-4">
          {topCurrencies.map((currency) => (
            baseCurrency !== currency ? (
              <CurrencyRow key={currency} base={baseCurrency} target={currency} />
            ) : null
          ))}
        </ul>
      </div>
      <div className="mt-4 text-xs text-gray-400 text-center border-t border-gray-100 pt-4">
        Rates fetched dynamically
      </div>
    </div>
  );
};
