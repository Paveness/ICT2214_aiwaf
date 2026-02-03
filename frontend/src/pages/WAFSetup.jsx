import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Globe, 
  Settings, 
  Rocket, 
  ShieldCheck, 
  Loader2, 
  ChevronRight, 
  ChevronLeft,
  Server,
  Lock
} from 'lucide-react';

const WAFSetup = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [progress, setProgress] = useState(0);

  const [formData, setFormData] = useState({
    targetIp: '',
    wafMode: 'shadow',
    wafPort: '8080',
    username: '',
    password: '',
    loginUsername: '',
    loginPassword: '',
    loginEndpoint: '',
    escapeEndpoint: ''
  });

  // Fixed Step 4 Logic: Move to Step 5 on completion
  useEffect(() => {
    if (step === 4) {
      setProgress(0); // Reset progress when starting deployment
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setTimeout(() => setStep(5), 800); // FIXED: Move to Step 5
            return 100;
          }
          return prev + 2; // Slightly faster for better UX
        });
      }, 50);
      return () => clearInterval(interval);
    }
  }, [step]);

  const handleNext = () => setStep(step + 1);
  const handleBack = () => setStep(step - 1);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-xl w-full bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
        
        <div className="bg-gray-900 p-8 text-white text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-500 rounded-xl shadow-lg shadow-blue-500/30">
              <ShieldCheck size={32} />
            </div>
          </div>
          <h1 className="text-2xl font-bold">Neuro-WAF Setup</h1>
          <p className="text-gray-400 text-sm mt-1">Configure your AI-powered protection layer</p>
          
          <div className="flex justify-center mt-6 gap-2">
            {[1, 2, 3, 4, 5].map((s) => (
              <div 
                key={s} 
                className={`h-1 w-12 rounded-full transition-colors ${step >= s ? 'bg-blue-500' : 'bg-gray-700'}`}
              />
            ))}
          </div>
        </div>

        <div className="p-8">
          {/* STEP 1: TARGET IP */}
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
              <div className="space-y-2">
                <label className="text-sm font-bold text-gray-700 flex items-center gap-2">
                  <Globe size={16} /> Web Server IP Address
                </label>
                <input 
                  type="text" 
                  placeholder="e.g. 192.168.1.100"
                  className="w-full p-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  value={formData.targetIp}
                  onChange={(e) => setFormData({...formData, targetIp: e.target.value})}
                />
              </div>
              <button 
                onClick={handleNext}
                disabled={!formData.targetIp}
                className="w-full py-4 bg-gray-900 text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-black transition-all disabled:opacity-50"
              >
                Continue to Configuration <ChevronRight size={18} />
              </button>
            </div>
          )}

          {/* STEP 2: CONFIGURATIONS */}
          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-700 flex items-center gap-2">
                    <Settings size={16} /> WAF Mode
                  </label>
                  <select 
                    className="w-full p-3 rounded-lg border border-gray-200 outline-none"
                    value={formData.wafMode}
                    onChange={(e) => setFormData({...formData, wafMode: e.target.value})}
                  >
                    <option value="shadow">Shadow (Logging Only)</option>
                    <option value="protect">Protect (Active Blocking)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-700 flex items-center gap-2">
                    <Server size={16} /> Proxy Port
                  </label>
                  <input 
                    type="number" 
                    placeholder="8080"
                    className="w-full p-3 rounded-lg border border-gray-200 outline-none"
                    value={formData.wafPort}
                    onChange={(e) => setFormData({...formData, wafPort: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-4 pt-4 border-t border-gray-100">
                <label className="text-sm font-bold text-gray-700 flex items-center gap-2">
                  <Lock size={16} /> Admin Credentials
                </label>
                <input 
                  type="text" placeholder="Username"
                  className="w-full p-3 rounded-lg border border-gray-200 outline-none"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                />
                <input 
                  type="password" placeholder="Password"
                  className="w-full p-3 rounded-lg border border-gray-200 outline-none"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                />
              </div>

              <div className="flex gap-3">
                <button onClick={handleBack} className="px-6 py-4 bg-gray-100 text-gray-600 rounded-xl font-bold hover:bg-gray-200 transition-all">
                  <ChevronLeft size={20} />
                </button>
                <button onClick={handleNext} className="flex-1 py-4 bg-blue-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-blue-700 shadow-lg shadow-blue-500/20">
                  Crawler Settings <Rocket size={18} />
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: CRAWLER SETTINGS */}
          {step === 3 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div className="space-y-4 pt-4">
                <label className="text-sm font-bold text-gray-900 flex items-center gap-2 uppercase tracking-wider">
                  <Rocket size={16} className="text-blue-500" /> Crawler Settings
                </label>
                
                <div className="grid grid-cols-2 gap-3">
                  <input 
                    type="text" placeholder="Login Username"
                    className="w-full p-3 rounded-lg border border-gray-200 outline-none text-sm"
                    value={formData.loginUsername}
                    onChange={(e) => setFormData({...formData, loginUsername: e.target.value})}
                  />
                  <input 
                    type="password" placeholder="Login Password"
                    className="w-full p-3 rounded-lg border border-gray-200 outline-none text-sm"
                    value={formData.loginPassword}
                    onChange={(e) => setFormData({...formData, loginPassword: e.target.value})}
                  />
                </div>

                <div className="space-y-3">
                  <div className="relative">
                    <span className="absolute inset-y-0 left-3 flex items-center text-gray-400 text-xs font-mono">POST</span>
                    <input 
                      type="text" placeholder="Login Endpoint (e.g. /api/login)"
                      className="w-full p-3 pl-14 rounded-lg border border-gray-200 outline-none text-sm"
                      value={formData.loginEndpoint}
                      onChange={(e) => setFormData({...formData, loginEndpoint: e.target.value})}
                    />
                  </div>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-3 flex items-center text-gray-400 text-xs font-mono">GET</span>
                    <input 
                      type="text" placeholder="Escape Endpoint (e.g. /logout)"
                      className="w-full p-3 pl-14 rounded-lg border border-gray-200 outline-none text-sm"
                      value={formData.escapeEndpoint}
                      onChange={(e) => setFormData({...formData, escapeEndpoint: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button onClick={handleBack} className="px-6 py-4 bg-gray-100 text-gray-600 rounded-xl font-bold hover:bg-gray-200 transition-all">
                  <ChevronLeft size={20} />
                </button>
                <button onClick={handleNext} className="flex-1 py-4 bg-blue-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-blue-700 shadow-lg shadow-blue-500/20">
                  Deploy <Rocket size={18} />
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: DEPLOYING */}
          {step === 4 && (
            <div className="py-10 text-center space-y-6 animate-in zoom-in-95">
              <Loader2 size={48} className="text-blue-500 animate-spin mx-auto" />
              <div>
                <h3 className="text-xl font-bold text-gray-800">Deploying Neuro-WAF</h3>
                <p className="text-sm text-gray-500 mt-2">
                  {progress < 40 ? 'Initializing proxy bridge...' : 
                   progress < 70 ? 'Running automated crawler...' : 
                   'Training AI Anomaly Engine...'}
                </p>
              </div>
              <div className="space-y-2">
                <div className="w-full bg-gray-100 h-3 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full transition-all duration-300" style={{ width: `${progress}%` }} />
                </div>
                <span className="text-xs font-bold text-gray-400">{progress}% Complete</span>
              </div>
            </div>
          )}

          {/* STEP 5: SUCCESS */}
          {step === 5 && (
            <div className="py-6 text-center space-y-6 animate-in fade-in scale-100">
              <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto shadow-inner">
                <ShieldCheck size={40} />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-800">Activation Ready</h3>
                <p className="text-sm text-gray-500 mt-2 px-6">
                  Neuro-WAF is now listening on port {formData.wafPort}. The AI model has been initialized with the application baseline.
                </p>
              </div>
              <button onClick={() => navigate('/login')} className="w-full py-4 bg-gray-900 text-white rounded-xl font-bold hover:bg-black transition-all">
                Proceed to Login
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WAFSetup;