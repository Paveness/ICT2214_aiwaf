// Main Dashboard with quick overview of key metrics
// src/pages/Overview.jsx
import React from 'react';
import { Globe, Target, ShieldCheck } from 'lucide-react';
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// --- MOCK DATA ---
const timelineData = Array.from({ length: 15 }, (_, i) => ({
  date: `Day ${i + 1}`,
  critical: Math.floor(Math.random() * 4000) + 1000,
  high: Math.floor(Math.random() * 2000) + 500,
}));

const attackLevelData = [
  { name: 'Critical', value: 115252, color: '#EF4444' }, 
  { name: 'High', value: 89898, color: '#F59E0B' },    
];

const StatCard = ({ title, value, subtext, icon: Icon, color, bg }) => (
  <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between h-36 relative overflow-hidden group hover:shadow-md transition-shadow">
    <div className={`absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity ${bg}`}>
      <Icon size={80} />
    </div>
    <div className="text-gray-500 text-xs font-bold uppercase tracking-wider z-10">{title}</div>
    <div className="flex items-end gap-3 z-10">
      <div className={`p-3 rounded-lg ${bg} ${color}`}>
        <Icon size={24} />
      </div>
      <div>
        <div className="text-3xl font-bold text-gray-800 leading-none">{value}</div>
        <div className="text-xs text-gray-500 mt-1">{subtext}</div>
      </div>
    </div>
  </div>
);

export default function Overview() {
  return (
    <div className="space-y-6">
      
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Total HTTP Traffic" value="1.1M" subtext="Requests in last 24h" icon={Globe} color="text-indigo-600" bg="bg-indigo-50" />
        <StatCard title="Threats Detected" value="35" subtext="20 High | 15 Critical" icon={Target} color="text-red-600" bg="bg-red-50" />
        <StatCard title="WAF Actions" value="205.2K" subtext="Requests Blocked" icon={ShieldCheck} color="text-emerald-600" bg="bg-emerald-50" />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-96">
        
        {/* Attacks Timeline */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 lg:col-span-2 flex flex-col">
          <h3 className="text-gray-800 font-bold mb-6">Attacks Timeline</h3>
          <div className="flex-1 w-full min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timelineData} barSize={20}>
                <XAxis dataKey="date" hide />
                <Tooltip cursor={{fill: '#f3f4f6'}} contentStyle={{borderRadius: '8px', border: 'none'}} />
                <Bar dataKey="critical" stackId="a" fill="#EF4444" radius={[0, 0, 4, 4]} />
                <Bar dataKey="high" stackId="a" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Attack Severity Donut */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col">
          <h3 className="text-gray-800 font-bold mb-2">Severity Distribution</h3>
          <div className="flex-1 relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={attackLevelData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" stroke="none">
                  {attackLevelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            {/* Center Text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-3xl font-bold text-gray-800">205K</span>
              <span className="text-xs text-gray-500 uppercase font-semibold">Blocked</span>
            </div>
          </div>
          {/* Legend */}
          <div className="flex justify-center gap-4 mt-2">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="w-3 h-3 rounded-full bg-red-500"></span> Critical
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="w-3 h-3 rounded-full bg-yellow-500"></span> High
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}