import React from 'react';
import { LogOut, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export const AppHeader = () => {
  const { logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center">
        {/* Placeholder for left side elements like a mobile menu button */}
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-gray-700">
          <div className="bg-blue-100 p-1.5 rounded-full text-blue-600">
            <User size={18} />
          </div>
          <span className="text-sm font-medium">{'Admin User'}</span>
        </div>
        <div className="h-6 w-px bg-gray-200 mx-2"></div>
        <button 
          onClick={logout}
          className="text-gray-500 hover:text-red-600 flex items-center gap-2 transition-colors"
        >
          <LogOut size={18} />
          <span className="text-sm font-medium hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
};
