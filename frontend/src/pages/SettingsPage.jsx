// src/pages/SettingsPage.jsx
import React, { useState } from 'react';
import { 
  User, 
  Bell, 
  Lock, 
  Shield, 
  Key, 
  Globe, 
  Smartphone, 
  Mail,
  Save
} from 'lucide-react';

const Toggle = ({ enabled, setEnabled }) => (
  <button
    onClick={() => setEnabled(!enabled)}
    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
      enabled ? 'bg-blue-600' : 'bg-gray-200'
    }`}
  >
    <span
      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
        enabled ? 'translate-x-6' : 'translate-x-1'
      }`}
    />
  </button>
);

const SectionHeader = ({ icon: Icon, title, description }) => (
  <div className="mb-6">
    <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
      <Icon size={20} className="text-blue-500" />
      {title}
    </h3>
    <p className="text-sm text-gray-500 ml-7">{description}</p>
  </div>
);

const SettingsPage = () => {
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [smsAlerts, setSmsAlerts] = useState(false);
  const [autoMitigation, setAutoMitigation] = useState(true);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">System Configuration</h1>
        <button className="flex items-center gap-2 bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-black transition-colors">
          <Save size={16} /> Save Changes
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Profile & Account */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <SectionHeader icon={User} title="Analyst Profile" description="Manage your account details." />
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Display Name</label>
                <input type="text" defaultValue="Admin User" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Role</label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-gray-50 text-gray-500 cursor-not-allowed" disabled>
                  <option>SOC Analyst (Tier 3)</option>
                  <option>System Administrator</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <SectionHeader icon={Key} title="API Keys" description="Manage access tokens." />
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100 mb-3">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-gray-700">Production Key</span>
                <span className="text-[10px] font-mono text-gray-500">pk_live_...9f2a</span>
              </div>
              <button className="text-xs text-red-600 font-semibold hover:underline">Revoke</button>
            </div>
            <button className="w-full py-2 border border-dashed border-gray-300 rounded-lg text-xs font-bold text-gray-500 hover:bg-gray-50 transition-colors">
              + Generate New Token
            </button>
          </div>
        </div>

        {/* Middle & Right: Settings Categories */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Notifications */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <SectionHeader icon={Bell} title="Alert Notifications" description="Configure how you receive critical security alerts." />
            
            <div className="space-y-4 divide-y divide-gray-100">
              <div className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Mail size={18} /></div>
                  <div>
                    <p className="text-sm font-bold text-gray-800">Email Reports</p>
                    <p className="text-xs text-gray-500">Receive daily summaries and high-priority alerts.</p>
                  </div>
                </div>
                <Toggle enabled={emailAlerts} setEnabled={setEmailAlerts} />
              </div>

              <div className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-50 text-purple-600 rounded-lg"><Smartphone size={18} /></div>
                  <div>
                    <p className="text-sm font-bold text-gray-800">SMS / PagerDuty</p>
                    <p className="text-xs text-gray-500">Immediate alerts for DDoS attacks exceeding 1Gbps.</p>
                  </div>
                </div>
                <Toggle enabled={smsAlerts} setEnabled={setSmsAlerts} />
              </div>
            </div>
          </div>

          {/* Security & Mitigation */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <SectionHeader icon={Shield} title="Global Security Policies" description="Apply system-wide protection rules." />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors cursor-pointer">
                <div className="flex justify-between items-start mb-2">
                  <Globe size={20} className="text-gray-400" />
                  <Toggle enabled={autoMitigation} setEnabled={setAutoMitigation} />
                </div>
                <h4 className="font-bold text-sm text-gray-800">Geo-Blocking</h4>
                <p className="text-xs text-gray-500 mt-1">Automatically block traffic from high-risk regions based on threat intel.</p>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors cursor-pointer">
                <div className="flex justify-between items-start mb-2">
                  <Lock size={20} className="text-gray-400" />
                  <Toggle enabled={true} setEnabled={() => {}} />
                </div>
                <h4 className="font-bold text-sm text-gray-800">Strict Rate Limiting</h4>
                <p className="text-xs text-gray-500 mt-1">Enforce aggressive API limits on unauthenticated endpoints.</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default SettingsPage;