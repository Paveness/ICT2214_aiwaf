// Top search bar and filters
// src/components/common/Header.jsx
import React from 'react';
import { useLocation } from 'react-router-dom';
import { Search, Bell } from 'lucide-react';

export default function Header() {
  const location = useLocation();

  // Helper to format pathname into a title (e.g., "/traffic" -> "Traffic Analysis")
  const getTitle = () => {
    switch(location.pathname) {
      case '/': return 'Dashboard Overview';
      case '/traffic': return 'Traffic Analysis';
      case '/ddos': return 'DDoS Mitigation';
      case '/events': return 'Security Events';
      default: return 'Neuro-WAF';
    }
  };

  return (
    <header className="bg-white h-16 border-b border-gray-200 flex items-center justify-between px-6 shadow-sm z-10">
      <h1 className="text-xl font-bold text-gray-800 tracking-tight">
        {getTitle()}
      </h1>

      <div className="flex items-center gap-6">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
          <input 
            type="text" 
            placeholder="Search logs, IPs..." 
            className="pl-10 pr-4 py-1.5 bg-gray-100 border-transparent focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 rounded-md text-sm transition-all outline-none w-64"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
          <Bell size={20} />
          <span className="absolute top-1.5 right-2 h-2 w-2 bg-red-500 rounded-full border border-white"></span>
        </button>

        {/* User Profile */}
        <div className="h-8 w-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-md cursor-pointer">
          JD
        </div>
      </div>
    </header>
  );
}