import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { MethodBadge, StatusBadge } from '../components/StatusBadge';
import {
  Compass,
  Search,
  Filter,
  RefreshCw,
  Radio,
  FileCode,
  Shield,
  AlertTriangle,
  ChevronRight,
  X
} from 'lucide-react';

export const ApiDiscovery = () => {
  const [endpoints, setEndpoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [methodFilter, setMethodFilter] = useState('');
  const [classFilter, setClassFilter] = useState('');
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [scanning, setScanning] = useState(false);

  const fetchEndpoints = async () => {
    try {
      setLoading(true);
      const params = {};
      if (search) params.search = search;
      if (methodFilter) params.method = methodFilter;
      if (classFilter) params.classification = classFilter;

      const res = await api.get('/discovery/endpoints', { params });
      setEndpoints(res.data);
    } catch (err) {
      console.error('Failed to load endpoints:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEndpoints();
  }, [search, methodFilter, classFilter]);

  const triggerRecon = async () => {
    try {
      setScanning(true);
      const res = await api.post('/discovery/scan/1');
      alert(`Recon Scan Completed! Mapped ${res.data.details.total_endpoints_discovered} API endpoints.`);
      fetchEndpoints();
    } catch (err) {
      alert('Recon error: ' + err.message);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-cyan-400" />
            <span>API Discovery & Reconnaissance</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Agent 2 (Recon Discovery) autonomous mapping of staging travel routes, parameters, and auth requirements.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={triggerRecon}
            disabled={scanning}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white flex items-center gap-2 shadow-lg shadow-cyan-600/20 transition-all font-mono"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
            <span>{scanning ? 'Discovering...' : 'Trigger Recon Scan (Agent 2)'}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="cyber-card rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search API path or summary (e.g. /bookings, hotels)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-700/80 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Method Filter */}
          <select
            value={methodFilter}
            onChange={(e) => setMethodFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-700/80 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
          >
            <option value="">All HTTP Methods</option>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>

          {/* Classification Filter */}
          <select
            value={classFilter}
            onChange={(e) => setClassFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-700/80 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
          >
            <option value="">All Classifications</option>
            <option value="active">Active APIs</option>
            <option value="zombie">Zombie APIs</option>
            <option value="shadow">Shadow APIs</option>
          </select>
        </div>
      </div>

      {/* Endpoints Table */}
      <div className="cyber-card rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Method</th>
                <th className="py-3 px-4">Endpoint Path</th>
                <th className="py-3 px-4">Summary</th>
                <th className="py-3 px-4">Auth Required</th>
                <th className="py-3 px-4">Classification</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {endpoints.length > 0 ? (
                endpoints.map((ep) => (
                  <tr
                    key={ep.id}
                    onClick={() => setSelectedEndpoint(ep)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4">
                      <MethodBadge method={ep.method} />
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">
                      {ep.path}
                    </td>
                    <td className="py-3 px-4 text-slate-300 max-w-xs truncate">
                      {ep.summary || 'Staging Route'}
                    </td>
                    <td className="py-3 px-4">
                      {ep.auth_required ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-mono text-[11px]">
                          <Shield className="w-3.5 h-3.5" />
                          <span>{ep.required_roles || 'Enforced'}</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-rose-400 font-mono text-[11px]">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>Public / None</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={ep.classification} size="xs" />
                    </td>
                    <td className="py-3 px-4 font-mono font-bold">
                      <span className={ep.risk_score >= 8 ? 'text-rose-400' : ep.risk_score >= 5 ? 'text-amber-400' : 'text-slate-300'}>
                        {ep.risk_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button className="text-cyan-400 hover:text-cyan-300 font-mono text-xs flex items-center gap-1 ml-auto">
                        <span>Details</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    {loading ? 'Enumerating API inventory...' : 'No matching endpoints found. Click "Trigger Recon Scan" above.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Endpoint Details Drawer */}
      {selectedEndpoint && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex justify-end animate-fadeIn">
          <div className="w-full max-w-lg bg-[#0d1322] border-l border-slate-800 p-6 overflow-y-auto space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <MethodBadge method={selectedEndpoint.method} />
                <StatusBadge status={selectedEndpoint.classification} size="xs" />
              </div>
              <button
                onClick={() => setSelectedEndpoint(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div>
              <p className="text-xs text-slate-400 font-mono uppercase">Target Path</p>
              <p className="text-base font-mono font-bold text-white mt-1 break-all">
                {selectedEndpoint.path}
              </p>
              <p className="text-xs text-slate-300 mt-2">{selectedEndpoint.description || selectedEndpoint.summary}</p>
            </div>

            {selectedEndpoint.recommendation && (
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs">
                <p className="font-semibold text-amber-400 flex items-center gap-1.5 mb-1 font-mono">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Agent 3 Inventory Recommendation</span>
                </p>
                <p className="text-slate-300 leading-relaxed">{selectedEndpoint.recommendation}</p>
              </div>
            )}

            {/* Parameters */}
            <div>
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono mb-3">
                Detected Request Parameters ({selectedEndpoint.parameters?.length || 0})
              </h4>
              {selectedEndpoint.parameters && selectedEndpoint.parameters.length > 0 ? (
                <div className="space-y-2">
                  {selectedEndpoint.parameters.map((p) => (
                    <div key={p.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs flex justify-between items-center">
                      <div>
                        <div className="flex items-center gap-2 font-mono">
                          <span className="font-bold text-cyan-300">{p.name}</span>
                          <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[10px] text-slate-400 uppercase">
                            {p.in_location}
                          </span>
                          {p.is_required && (
                            <span className="text-[10px] text-rose-400 font-bold">REQUIRED</span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 mt-1 font-mono">Type: {p.data_type}</p>
                      </div>
                      {p.example_value && (
                        <div className="text-right font-mono text-[11px] text-slate-400">
                          ex: <span className="text-slate-200">{p.example_value}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">No request parameters required for this endpoint.</p>
              )}
            </div>

            {/* Metadata */}
            <div className="border-t border-slate-800 pt-4 text-xs font-mono space-y-2 text-slate-400">
              <div className="flex justify-between">
                <span>First Seen:</span>
                <span className="text-slate-200">{new Date(selectedEndpoint.first_seen).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Activity:</span>
                <span className="text-slate-200">{new Date(selectedEndpoint.last_seen).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span>Risk Score:</span>
                <span className="text-cyan-400 font-bold">{selectedEndpoint.risk_score} / 10.0</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

