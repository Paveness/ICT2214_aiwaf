import React, { useState, useEffect } from 'react';
import { 
  Search, RefreshCw, Eye, X, ArrowRight, Server, ChevronLeft, ChevronRight, ShieldAlert 
} from 'lucide-react';

const API_BASE_URL = "http://localhost:5000/api";

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
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("All");
  const [attackTypes, setAttackTypes] = useState([]);
  const [selectedLog, setSelectedLog] = useState(null);

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const ITEMS_PER_PAGE = 20;

  const fetchFilters = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/filters`);
      const data = await res.json();
      setAttackTypes(data);
    } catch (err) { console.error(err); }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const query = new URLSearchParams({
        search: searchTerm,
        attack_type: filterType,
        limit: ITEMS_PER_PAGE,
        page: currentPage // Send current page to backend
      }).toString();

      const res = await fetch(`${API_BASE_URL}/logs?${query}`);
      const data = await res.json();
      
      // Update state with new structure { logs: [], pagination: {} }
      setLogs(data.logs);
      setTotalPages(data.pagination.total_pages);
    } catch (err) {
      console.error("Failed to load logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchFilters(); }, []);

  // Reset to Page 1 if search/filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filterType]);

  // Fetch logs whenever page, search, or filter changes
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchLogs();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, filterType, currentPage]);

  return (
    <div className="space-y-6 relative pb-10">
      
      {/* Header Controls */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
        <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <ShieldAlert className="text-blue-600" /> Security Event Stream
        </h1>
        <div className="flex gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
            <input 
              type="text" 
              placeholder="Search IP or Path..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select 
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 rounded-lg border border-gray-200 text-sm bg-gray-50 text-gray-700 focus:outline-none cursor-pointer"
          >
            <option value="All">All Events</option>
            {attackTypes.map(t => <option key={t} value={t}>{t === 'None' ? 'Normal Traffic' : t}</option>)}
          </select>
          <button onClick={fetchLogs} className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-600">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Log Table */}
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
                <tr><td colSpan="6" className="p-8 text-center text-gray-500">No logs found.</td></tr>
              ) : logs.map((log) => (
                <tr key={log.id} className="hover:bg-blue-50/50 transition-colors">
                  <td className="px-6 py-3 whitespace-nowrap text-gray-600 font-mono text-xs">
                    {new Date(log.timestamp).toLocaleTimeString()}
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

        {/* Pagination Controls */}
        <div className="flex items-center justify-between px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            Page <span className="font-bold">{currentPage}</span> of <span className="font-bold">{totalPages}</span>
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
              disabled={currentPage === totalPages}
              className={`p-2 rounded-lg border ${currentPage === totalPages ? 'text-gray-300 border-gray-200 cursor-not-allowed' : 'text-gray-600 border-gray-300 hover:bg-white'}`}
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Inspector Modal (Same as before) */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-end">
          <div className="bg-white w-full max-w-md h-full shadow-2xl p-6 flex flex-col animate-slide-in-right">
             <div className="flex justify-between items-center mb-6 pb-4 border-b">
               <h2 className="text-xl font-bold text-gray-800">Event Details #{selectedLog.id}</h2>
               <button onClick={() => setSelectedLog(null)} className="p-2 hover:bg-gray-100 rounded-full"><X size={20} /></button>
             </div>
             <div className="space-y-6 flex-1 overflow-y-auto">
                {/* Details content... */}
                <div className="p-4 bg-gray-50 rounded font-mono text-sm">
                   <p>Timestamp: {new Date(selectedLog.timestamp).toLocaleString()}</p>
                   <p>Source: {selectedLog.source_ip} ({selectedLog.geo_location})</p>
                   <p>Target: {selectedLog.destination_ip}</p>
                   <p>Path: {selectedLog.request_path}</p>
                </div>
             </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventsLog;