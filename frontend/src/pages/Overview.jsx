// src/pages/Overview.jsx
import React from 'react';
import { 
  Globe, 
  ShieldAlert, 
  BrainCircuit, 
  Activity, 
  CheckCircle2, 
  AlertTriangle,
  Target
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  Legend,
  CartesianGrid
} from 'recharts';

// --- MOCK DATA BASED ON YOUR AI FEATURES ---
const hybridTimelineData = Array.from({ length: 10 }, (_, i) => ({
  date: `14:0${i}`,
  signature: Math.floor(Math.random() * 500) + 200,
  aiAnomaly: Math.floor(Math.random() * 300) + 50,
}));

const featureContributionData = [
  { name: 'Query Suspicious Chars', value: 85 }, // From query_suspicious_char_count
  { name: 'Path Hex Encoding', value: 65 },     // From path_hex_pct_count
  { name: 'Body Length Anomaly', value: 45 },    // From body_len
  { name: 'Path Entropy', value: 30 },
  { name: 'Header Count', value: 20 },           // From header_count
].sort((a, b) => b.value - a.value);

const attackLevelData = [
  { name: 'Signature Block', value: 65, color: '#3B82F6' }, // Blue
  { name: 'AI Anomaly Block', value: 35, color: '#8B5CF6' }, // Purple
];

// --- SUB-COMPONENTS ---
const StatCard = ({ title, value, subtext, icon: Icon, color, bg }) => (
  <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between h-36 relative overflow-hidden group hover:shadow-md transition-all">
    <div className={`absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity ${bg}`}>
      <Icon size={70} />
    </div>
    <div>
      <p className="text-gray-500 text-sm font-medium">{title}</p>
      <h3 className="text-2xl font-bold mt-1 text-gray-800">{value}</h3>
    </div>
    <p className={`text-xs font-semibold ${color}`}>{subtext}</p>
  </div>
);

const ModelHealth = () => (
  <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
    <div className="flex items-center justify-between mb-4">
      <h3 className="font-bold text-gray-800 flex items-center gap-2">
        <BrainCircuit size={18} className="text-purple-500" /> Model Health
      </h3>
      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full animate-pulse">
        LIVE
      </span>
    </div>
    <div className="space-y-3">
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-500">Active Model</span>
        <span className="font-mono text-gray-700">xgboost_v1.0.2.joblib</span>
      </div>
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-500">Last Retrained</span>
        <span className="text-gray-700">2 hours ago</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2 mt-2">
        <div className="bg-green-500 h-2 rounded-full w-[98%]"></div>
      </div>
      <p className="text-[10px] text-gray-400 text-center italic">Accuracy: 98.4% | Threshold: 0.85</p>
    </div>
  </div>
);

const Overview = () => {
  return (
    <div className="space-y-6">
      {/* 1. Metric Row - AI vs Signature */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Requests" 
          value="1.2M" 
          subtext="+12% from last hour" 
          icon={Activity} 
          color="text-blue-600" 
          bg="text-blue-500" 
        />
        <StatCard 
          title="Signature Blocks" 
          value="42,851" 
          subtext="Known Attack Patterns" 
          icon={ShieldAlert} 
          color="text-red-600" 
          bg="text-red-500" 
        />
        <StatCard 
          title="AI Anomaly Blocks" 
          value="12,104" 
          subtext="Zero-Day Detections" 
          icon={BrainCircuit} 
          color="text-purple-600" 
          bg="text-purple-500" 
        />
        <StatCard 
          title="Protection Score" 
          value="99.2%" 
          subtext="System Fully Optimized" 
          icon={CheckCircle2} 
          color="text-green-600" 
          bg="text-green-500" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 2. Main Chart: Hybrid Defense Timeline */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold text-gray-800">Hybrid Defense Timeline</h3>
            <div className="flex gap-4 text-xs">
              <span className="flex items-center gap-1 text-blue-500">● Signature</span>
              <span className="flex items-center gap-1 text-purple-500">● AI Anomaly</span>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hybridTimelineData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="signature" stackId="a" fill="#3B82F6" radius={[0, 0, 0, 0]} />
                <Bar dataKey="aiAnomaly" stackId="a" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Feature Explainability (XAI) Heatmap */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="font-bold text-gray-800 mb-6 flex items-center gap-2">
            <AlertTriangle size={18} className="text-amber-500" /> Explainability: Top Triggers
          </h3>
          <div className="space-y-6">
            {featureContributionData.map((feature) => (
              <div key={feature.name}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 font-medium">{feature.name}</span>
                  <span className="text-gray-400">{feature.value}% impact</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div 
                    className="bg-amber-400 h-2 rounded-full transition-all duration-500" 
                    style={{ width: `${feature.value}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-8 text-[11px] text-gray-400 leading-tight">
            These features represent the highest contributors to the current anomaly probability score across all intercepted requests.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* 4. Attack Distribution */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-gray-800 font-bold mb-4">Block Distribution</h3>
          <div className="h-48 relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={attackLevelData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" stroke="none">
                  {attackLevelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-2xl font-bold text-gray-800">54K</span>
              <span className="text-[10px] text-gray-400 uppercase font-bold">Total Blocks</span>
            </div>
          </div>
          <div className="flex justify-center gap-6 mt-2 text-xs">
            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-blue-500"></span> Signature</div>
            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-purple-500"></span> AI Anomaly</div>
          </div>
        </div>

        {/* 5. Target Highlights */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-gray-800 font-bold mb-4 flex items-center gap-2">
            <Target size={18} className="text-red-500" /> High-Risk Endpoints
          </h3>
          <div className="space-y-4">
            {['/api/v1/login', '/wp-admin/php', '/api/users/profile'].map((path) => (
              <div key={path} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded-lg transition-colors border-b border-gray-50 last:border-0">
                <code className="text-xs text-blue-600 font-medium">{path}</code>
                <span className="text-xs font-bold text-gray-700 bg-gray-100 px-2 py-1 rounded">High Anomaly</span>
              </div>
            ))}
          </div>
        </div>

        {/* 6. Model Health Widget */}
        <ModelHealth />
      </div>
    </div>
  );
};

export default Overview;