// Multidimensional Traffic Analysis Page from inspired from AWS
// src/pages/TrafficAnalysis.jsx
import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Globe, Server, Zap, Activity } from 'lucide-react';

// --- MOCK DATA ---
const bandwidthData = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}:00`,
  ingress: Math.floor(Math.random() * 500) + 200,
  egress: Math.floor(Math.random() * 300) + 100,
}));

const trafficShapeData = [
  { subject: 'SQL Injection', A: 120, fullMark: 150 },
  { subject: 'XSS', A: 98, fullMark: 150 },
  { subject: 'Bot Traffic', A: 86, fullMark: 150 },
  { subject: 'DDoS', A: 99, fullMark: 150 },
  { subject: 'Path Traversal', A: 85, fullMark: 150 },
  { subject: 'Valid API', A: 65, fullMark: 150 },
];

// --- COMPONENTS ---
const MetricCard = ({ label, value, trend, isPositive }) => (
  <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
    <div>
      <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider">{label}</p>
      <h3 className="text-2xl font-bold text-gray-800 mt-1">{value}</h3>
    </div>
    <div className={`flex items-center gap-1 text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'} bg-gray-50 px-2 py-1 rounded-md`}>
      {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
      {trend}
    </div>
  </div>
);

export default function TrafficAnalysis() {
  return (
    <div className="space-y-6">
      
      {/* 1. Top Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard label="Total Bandwidth" value="45.2 GB" trend="+12.5%" isPositive={false} />
        <MetricCard label="Request Latency" value="42 ms" trend="-5.0%" isPositive={true} />
        <MetricCard label="Cache Hit Ratio" value="94.2%" trend="+1.2%" isPositive={true} />
      </div>

      {/* 2. Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-96">
        
        {/* Left: Bandwidth Area Chart (2/3 width) */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm lg:col-span-2 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold text-gray-800 flex items-center gap-2">
              <Activity size={18} className="text-indigo-500"/> Traffic Volume (24h)
            </h3>
            <select className="text-sm border-gray-200 border rounded-md px-2 py-1 text-gray-600 outline-none">
              <option>Last 24 Hours</option>
              <option>Last 7 Days</option>
            </select>
          </div>
          
          <div className="flex-1 w-full min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={bandwidthData}>
                <defs>
                  <linearGradient id="colorIngress" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorEgress" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="time" tick={{fontSize: 12, fill: '#9ca3af'}} axisLine={false} tickLine={false} />
                <YAxis tick={{fontSize: 12, fill: '#9ca3af'}} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}} />
                <Legend iconType="circle" />
                <Area type="monotone" dataKey="ingress" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorIngress)" name="Inbound (MB)" />
                <Area type="monotone" dataKey="egress" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorEgress)" name="Outbound (MB)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Threat Radar (1/3 width) */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
          <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
            <Zap size={18} className="text-orange-500"/> Threat Vector Shape
          </h3>
          <p className="text-xs text-gray-500 mb-4">Multidimensional view of current attack types.</p>
          
          <div className="flex-1 w-full min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={trafficShapeData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 10, fontWeight: 600 }} />
                <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
                <Radar name="Threat Score" dataKey="A" stroke="#f43f5e" strokeWidth={2} fill="#f43f5e" fillOpacity={0.5} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3. Bottom Geo-Distribution Row */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Globe size={18} className="text-blue-500"/> Geographic Distribution
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['United States', 'China', 'Russia', 'Germany'].map((country, i) => (
            <div key={country} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="flex items-center gap-3">
                <span className="text-lg">{'🇺🇸 🇨🇳 🇷🇺 🇩🇪'.split(' ')[i]}</span>
                <span className="text-sm font-medium text-gray-700">{country}</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{Math.floor(Math.random() * 50) + 10}%</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}