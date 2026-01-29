// Left navigation bar to access different sections of the application
// src/components/common/Sidebar.jsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ShieldAlert, Activity, FileText, LifeBuoy, Settings } from 'lucide-react';

const SidebarItem = ({ to, icon: Icon, label }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `flex flex-col items-center justify-center py-4 w-full transition-all duration-200 border-l-4 ${
        isActive
          ? 'bg-slate-800 border-indigo-500 text-white shadow-[inset_0px_0px_20px_rgba(0,0,0,0.2)]'
          : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
      }`
    }
  >
    <Icon size={24} strokeWidth={1.5} />
    <span className="text-[10px] mt-1.5 font-medium tracking-wide uppercase">{label}</span>
  </NavLink>
);

export default function Sidebar() {
  return (
    <aside className="w-20 bg-slate-900 text-white flex flex-col items-center py-6 shadow-xl z-20">
      {/* Logo */}
      <div className="mb-8 w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/30 font-bold text-lg tracking-tighter">
        NW
      </div>

      {/* Navigation */}
      <nav className="flex-1 w-full flex flex-col gap-1">
        <SidebarItem to="/" icon={LayoutDashboard} label="Overview" />
        <SidebarItem to="/ddos" icon={ShieldAlert} label="DDoS" />
        <SidebarItem to="/events" icon={FileText} label="Events" />
        <SidebarItem to="/traffic" icon={Activity} label="Traffic" />
      </nav>

      {/* Bottom Actions */}
      <div className="mt-auto w-full flex flex-col gap-1">
        <SidebarItem to="/support" icon={LifeBuoy} label="Help" />
        <button className="p-4 text-slate-500 hover:text-white transition-colors">
          <Settings size={20} />
        </button>
      </div>
    </aside>
  );
}