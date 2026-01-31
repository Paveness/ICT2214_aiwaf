// View of DDos attack statistics and mitigation controls
// src/pages/DDoSDashboard.jsx
import React, { useState } from 'react';
import { 
  Zap, 
  ShieldCheck, 
  ShieldAlert, 
  Activity, 
  Settings2, 
  MapPin, 
  Clock, 
  Lock
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';

// --- MOCK DATA: LIVE TRAFFIC VS. TRAINED BASELINE ---
const liveTrafficData = Array.from({ length: 24 }, (_, i) => {
  const baseline = Math.floor(Math.random() * 200) + 100;
  const current = i > 15 && i < 20 ? baseline * 4 : baseline + (Math.random() * 50); // Simulated Spike
  return {
    time: `${i}:00`,
    currentRPS: current,
    baselineRPS: baseline,
    dropped: current > baseline * 2 ? current - (baseline * 2) : 0,
  };
});

const topAttackers = [
  { ip: '192.168.1.45', score: 0.98, rps: 450, region: 'RU' },
  { ip: '45.22.11.90', score: 0.95, rps: 310, region: 'CN' },
  { ip: '103.4.55.1', score: 0.88, rps: 280, region: 'BR' },
  { ip: '89.1.2.33', score: 0.82, rps: 150, region: 'UA' },
];

const DDoSDashboard = () => {
  const [isMitigationActive, setMitigation] = useState(true);
  const [aiThreshold, setThreshold] = useState(0.85);

  return (
    <div className="space-y-6">
      {/* 1. Mitigation Status Header */}
      <div className={`p-6 rounded-xl border flex items-center justify-between transition-colors ${
        isMitigationActive ? 'bg-green-50 border-green-200' : 'bg-amber-50 border-amber-200'
      }`}>
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-full ${isMitigationActive ? 'bg-green-500' : 'bg-amber-500'} text-white`}>
            {isMitigationActive ? <ShieldCheck size={24} /> : <ShieldAlert size={24} />}
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">
              DDoS Protection: {isMitigationActive ? 'Active & Filtering' : 'Monitoring Only'}
            </h2>
            <p className="text-sm text-gray-600">
              Current Mode: <span className="font-semibold">Adaptive AI Rate-Limiting</span>
            </p>
          </div>
        </div>
        <button 
          onClick={() => setMitigation(!isMitigationActive)}
          className={`px-6 py-2 rounded-lg font-bold text-white transition-all ${
            isMitigationActive ? 'bg-red-500 hover:bg-red-600' : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {isMitigationActive ? 'DISABLE MITIGATION' : 'ENABLE MITIGATION'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 2. Main Chart: Requests vs Baseline */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="font-bold text-gray-800 flex items-center gap-2">
                <Activity size={18} className="text-blue-500" /> Real-time Traffic vs. Baseline
              </h3>
              <p className="text-xs text-gray-400">Comparing live RPS against trained application behavior</p>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={liveTrafficData}>
                <defs>
                  <linearGradient id="colorCurrent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorDropped" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} />
                <Tooltip />
                <Area type="monotone" dataKey="baselineRPS" stroke="#94a3b8" fill="transparent" strokeDasharray="5 5" name="Baseline (Normal)" />
                <Area type="monotone" dataKey="currentRPS" stroke="#3B82F6" fillOpacity={1} fill="url(#colorCurrent)" name="Live Requests" />
                <Area type="monotone" dataKey="dropped" stroke="#EF4444" fillOpacity={1} fill="url(#colorDropped)" name="AI Dropped Traffic" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. AI Threshold Tuning (Unique Value Prop) */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col">
          <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Settings2 size={18} className="text-purple-500" /> AI Sensitivity Control
          </h3>
          <div className="flex-1 space-y-8">
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
              <div className="flex justify-between mb-2">
                <label className="text-sm font-semibold text-gray-700">Block Probability Threshold</label>
                <span className="text-purple-600 font-mono font-bold">{aiThreshold}</span>
              </div>
              <input 
                type="range" min="0.5" max="0.99" step="0.01" value={aiThreshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
              <div className="flex justify-between text-[10px] text-gray-400 mt-2">
                <span>Aggressive (Low FP)</span>
                <span>Conservative (High Security)</span>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Active Modules</h4>
              {[
                { label: 'Volumetric Rate Limiter', active: true },
                { label: 'Behavioral Bot Detection', active: true },
                { label: 'Zombie-Request Filtering', active: false },
              ].map((mod) => (
                <div key={mod.label} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{mod.label}</span>
                  <div className={`w-8 h-4 rounded-full relative transition-colors ${mod.active ? 'bg-blue-500' : 'bg-gray-300'}`}>
                    <div className={`absolute top-1 w-2 h-2 bg-white rounded-full transition-all ${mod.active ? 'right-1' : 'left-1'}`}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <button className="w-full mt-6 py-3 bg-gray-900 text-white rounded-lg text-sm font-bold flex items-center justify-center gap-2 hover:bg-black transition-colors">
            <Lock size={16} /> Deploy New Policy
          </button>
        </div>
      </div>

      {/* 4. Top Malicious Sources Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <h3 className="font-bold text-gray-800">Top Anomalous Traffic Sources</h3>
        </div>
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase font-bold">
            <tr>
              <th className="px-6 py-4">Source IP</th>
              <th className="px-6 py-4">Region</th>
              <th className="px-6 py-4">Peak RPS</th>
              <th className="px-6 py-4">AI Anomaly Score</th>
              <th className="px-6 py-4">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {topAttackers.map((attacker) => (
              <tr key={attacker.ip} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 font-mono text-sm font-bold text-gray-700">{attacker.ip}</td>
                <td className="px-6 py-4 text-sm text-gray-600 flex items-center gap-2">
                  <MapPin size={14} /> {attacker.region}
                </td>
                <td className="px-6 py-4 text-sm font-semibold text-red-500">{attacker.rps} r/s</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-100 rounded-full h-1.5 w-24">
                      <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${attacker.score * 100}%` }}></div>
                    </div>
                    <span className="text-xs font-bold text-purple-600">{attacker.score}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-red-100 text-red-700 text-[10px] font-bold rounded">BLOCKED</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DDoSDashboard;