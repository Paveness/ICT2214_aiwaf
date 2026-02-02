import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, RefreshCw, Eye, X, Server, ChevronLeft, ChevronRight, ShieldAlert, Clock, Calendar, Zap 
} from 'lucide-react';

const API_BASE_URL = "http://localhost:5000/api";

// Helper to get local time string for MySQL (YYYY-MM-DD HH:MM:SS)
const getLocalMySQLTime = () => {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000; // Offset in milliseconds
  return new Date(now.getTime() - offset).toISOString().slice(0, 19).replace('T', ' ');
};

const getActionColor = (action) => {
  switch (action.toUpperCase()) {
    case 'BLOCKED': return 'bg-red-100 text-red-700 border-red-200';
    case 'ALLOWED': return 'bg-green-100 text-green-700 border-green-200';
    case 'FLAGGED': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    default: return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

const EventsLog = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("All");
  const [attackTypes, setAttackTypes] = useState([]);
  
  // TIME FILTER STATE
  const [timeMode, setTimeMode] = useState("preset"); 
  const [timePreset, setTimePreset] = useState("24h");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  
  // NEW: Track when "Live Mode" started to hide old logs
  const [liveStartTime, setLiveStartTime] = useState(null);

  const [selectedLog, setSelectedLog] = useState(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const ITEMS_PER_PAGE = 20;

  const liveIntervalRef = useRef(null);

  // 1. Handle Time Preset Change (The Logic Fix)
  const handleTimePresetChange = (e) => {
    const newValue = e.target.value;
    setTimePreset(newValue);

    if (newValue === 'live') {
      // If switching TO Live Mode:
      // 1. Capture the current local time as the "Zero Hour"
      const now = getLocalMySQLTime();
      setLiveStartTime(now);
      
      // 2. Clear the table visually so it looks like a fresh stream
      setLogs([]); 
    } else {
      // If switching AWAY from Live Mode, reset the start time
      setLiveStartTime(null);
    }
  };

  const fetchFilters = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/filters`);
      const data = await res.json();
      setAttackTypes(data);
    } catch (err) { console.error(err); }
  };

  const fetchLogs = async (isBackgroundRefresh = false) => {
    if (!isBackgroundRefresh) setLoading(true);
    
    try {
      const queryParams = {
        search: searchTerm,
        attack_type: filterType,
        limit: ITEMS_PER_PAGE,
        page: currentPage,
        time_mode: timeMode,
      };

      // --- MODIFIED LOGIC START ---
      if (timeMode === 'preset') {
        if (timePreset === 'live') {
          // If in Live Mode, DO NOT use 'preset'. 
          // Instead, switch to 'after' mode using our captured start time.
          if (!liveStartTime) return; // Wait for state to settle
          queryParams.time_mode = 'after';
          queryParams.start_date = liveStartTime;
        } else {
          // Normal preset (24h, 1h, etc.)
          queryParams.time_preset = timePreset;
        }
      }
      // --- MODIFIED LOGIC END ---

      if (timeMode === 'after' || timeMode === 'between') queryParams.start_date = startDate;
      if (timeMode === 'before' || timeMode === 'between') queryParams.end_date = endDate;

      const query = new URLSearchParams(queryParams).toString();
      const res = await fetch(`${API_BASE_URL}/logs?${query}`);
      const data = await res.json();
      
      // Safety check: ensure we didn't switch modes while fetching
      setLogs(data.logs);
      setTotalPages(data.pagination.total_pages);
    } catch (err) {
      console.error("Failed to load logs:", err);
    } finally {
      if (!isBackgroundRefresh) setLoading(false);
    }
  };

  useEffect(() => { fetchFilters(); }, []);

  useEffect(() => { setCurrentPage(1); }, [searchTerm, filterType, timeMode, timePreset, startDate, endDate]);

  // LIVE MONITORING LOOP
  useEffect(() => {
    // Immediate fetch when filters change
    // (We wrap in timeout to debounce slightly and allow state updates)
    const timer = setTimeout(() => {
      fetchLogs();
    }, 500);

    if (liveIntervalRef.current) clearInterval(liveIntervalRef.current);

    // Only start polling if we are in Live Mode AND have a start time
    if (timeMode === 'preset' && timePreset === 'live' && liveStartTime) {
      liveIntervalRef.current = setInterval(() => {
        fetchLogs(true);
      }, 2000);
    }

    return () => {
      clearTimeout(timer);
      if (liveIntervalRef.current) clearInterval(liveIntervalRef.current);
    };
  }, [searchTerm, filterType, timeMode, timePreset, startDate, endDate, currentPage, liveStartTime]); // Added liveStartTime

  return (
    <div className="space-y-6 relative pb-10">
      
      {/* HEADER */}
      <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2 min-w-fit">
          <ShieldAlert className="text-blue-600" /> 
          <h1 className="text-xl font-bold text-gray-800">Security Event Stream</h1>
          
          {timePreset === 'live' && timeMode === 'preset' && (
            <span className="flex items-center gap-1.5 px-2 py-1 bg-red-100 text-red-600 text-xs font-bold rounded-full animate-pulse ml-2">
              <span className="w-2 h-2 bg-red-600 rounded-full"></span>
              LIVE
            </span>
          )}
        </div>

        <div className="flex flex-wrap gap-3 w-full xl:justify-end items-center">
          
          <div className="flex items-center bg-gray-50 border border-gray-200 rounded-lg p-1">
            <select 
              value={timeMode} 
              onChange={(e) => setTimeMode(e.target.value)}
              className="bg-transparent text-sm font-medium text-gray-700 focus:outline-none px-2 py-1 cursor-pointer"
            >
              <option value="preset">Quick Range</option>
              <option value="between">Between Dates</option>
              <option value="after">After Date</option>
              <option value="before">Before Date</option>
            </select>
          </div>

          {timeMode === 'preset' && (
            <div className="relative">
              {timePreset === 'live' ? (
                 <Zap className="absolute left-3 top-1/2 -translate-y-1/2 text-red-500 fill-red-500" size={16} />
              ) : (
                 <Clock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
              )}
              
              <select 
                value={timePreset}
                onChange={handleTimePresetChange} // USE THE NEW HANDLER
                className={`pl-9 pr-8 py-2 rounded-lg border text-sm focus:outline-none cursor-pointer font-bold ${
                  timePreset === 'live' 
                    ? 'border-red-200 bg-red-50 text-red-700' 
                    : 'border-gray-200 bg-gray-50 text-gray-700'
                }`}
              >
                <option value="live">⚡️ Live Real-Time</option>
                <option disabled>──────────</option>
                <option value="5m">Last 5 Minutes</option>
                <option value="1h">Last 1 Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="all">All Time</option>
              </select>
            </div>
          )}

          {/* Date Pickers (Same as before) */}
          {(timeMode === 'after' || timeMode === 'between') && (
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
              <input 
                type="datetime-local" 
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="pl-9 pr-3 py-2 rounded-lg border border-gray-200 text-sm w-48" step="1"
              />
            </div>
          )}

          {timeMode === 'between' && <span className="text-gray-400 text-xs font-bold uppercase">TO</span>}

          {(timeMode === 'before' || timeMode === 'between') && (
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
              <input 
                type="datetime-local" 
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="pl-9 pr-3 py-2 rounded-lg border border-gray-200 text-sm w-48" step="1"
              />
            </div>
          )}

          <select 
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 rounded-lg border border-gray-200 text-sm bg-gray-50 text-gray-700 focus:outline-none"
          >
            <option value="All">All Attack Types</option>
            {attackTypes.map(t => <option key={t} value={t}>{t === 'None' ? 'Normal Traffic' : t}</option>)}
          </select>

          <button onClick={() => fetchLogs()} className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-600">
            <RefreshCw size={18} className={timePreset === 'live' ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {/* TABLE SECTION */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-gray-50 text-gray-500 text-xs uppercase font-bold tracking-wider">
              <tr>
                <th className="px-6 py-4">Time</th>
                <th className="px-6 py-4">Source</th>
                <th className="px-6 py-4">Destination</th>
                <th className="px-6 py-4">Attack Type</th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4 text-center">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {loading ? (
                <tr><td colSpan="6" className="p-8 text-center text-gray-500">Loading events...</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan="6" className="p-8 text-center text-gray-500">
                  {timePreset === 'live' ? "Waiting for new real-time events..." : "No logs found."}
                </td></tr>
              ) : logs.map((log) => (
                <tr key={log.id} className="hover:bg-blue-50/50 transition-colors animate-fade-in">
                  <td className="px-6 py-3 whitespace-nowrap text-gray-600 font-mono text-xs">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-gray-700">{log.source_ip}</span>
                      <span className="text-[10px] bg-gray-200 px-1.5 rounded text-gray-600">{log.geo_location}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-2">
                      <Server size={14} className="text-gray-400" />
                      <span className="font-mono text-gray-600">{log.destination_ip}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <span className={`text-xs font-semibold ${log.attack_type === 'None' ? 'text-gray-400' : 'text-red-600'}`}>
                      {log.attack_type === 'None' ? 'Clean' : log.attack_type}
                    </span>
                    <div className="text-[10px] text-gray-400 truncate max-w-[150px]">{log.request_path}</div>
                  </td>
                  <td className="px-6 py-3">
                    <span className={`px-2 py-1 text-[10px] font-bold rounded border ${getActionColor(log.action_taken)}`}>
                      {log.action_taken}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-center">
                    <button onClick={() => setSelectedLog(log)} className="text-gray-400 hover:text-blue-600">
                      <Eye size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* PAGINATION CONTROLS */}
        <div className="flex items-center justify-between px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            Page <span className="font-bold">{currentPage}</span> of <span className="font-bold">{totalPages || 1}</span>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className={`p-2 rounded-lg border ${currentPage === 1 ? 'text-gray-300 border-gray-200 cursor-not-allowed' : 'text-gray-600 border-gray-300 hover:bg-white'}`}
            >
              <ChevronLeft size={16} />
            </button>
            <button 
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages || totalPages === 0}
              className={`p-2 rounded-lg border ${currentPage === totalPages || totalPages === 0 ? 'text-gray-300 border-gray-200 cursor-not-allowed' : 'text-gray-600 border-gray-300 hover:bg-white'}`}
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* INSPECTOR MODAL (Same as before) */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-end">
          <div className="bg-white w-full max-w-md h-full shadow-2xl p-6 flex flex-col animate-slide-in-right">
             <div className="flex justify-between items-center mb-6 pb-4 border-b">
               <h2 className="text-xl font-bold text-gray-800">Event Details #{selectedLog.id}</h2>
               <button onClick={() => setSelectedLog(null)} className="p-2 hover:bg-gray-100 rounded-full"><X size={20} /></button>
             </div>
             <div className="space-y-6 flex-1 overflow-y-auto">
                <div className="p-4 bg-gray-50 rounded font-mono text-sm space-y-2">
                   <p><span className="font-bold text-gray-500">Time:</span> {new Date(selectedLog.timestamp).toLocaleString()}</p>
                   <p><span className="font-bold text-gray-500">Source:</span> {selectedLog.source_ip} ({selectedLog.geo_location})</p>
                   <p><span className="font-bold text-gray-500">Dest:</span> {selectedLog.destination_ip}</p>
                   <p><span className="font-bold text-gray-500">Path:</span> <br/>{selectedLog.request_path}</p>
                </div>
             </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventsLog;