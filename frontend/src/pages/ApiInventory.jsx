import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { MethodBadge, StatusBadge } from '../components/StatusBadge';
import { Layers, AlertTriangle, ShieldCheck, RefreshCw, FileText, CheckCircle2 } from 'lucide-react';

export const ApiInventory = () => {
  const [stats, setStats] = useState(null);
  const [endpoints, setEndpoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const [statsRes, epRes] = await Promise.all([
        api.get('/inventory/stats'),
        api.get('/discovery/endpoints')
      ]);
      setStats(statsRes.data);
      setEndpoints(epRes.data);
    } catch (err) {
      console.error('Failed to load inventory data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  const triggerReclassify = async () => {
    try {
      setRefreshing(true);
      await api.post('/inventory/reclassify/1');
      await fetchInventory();
      alert('API Inventory reclassification completed by Agent 3!');
    } catch (err) {
      alert('Reclassification failed: ' + err.message);
    } finally {
      setRefreshing(false);
    }
  };

  const updateClassification = async (endpointId, newClass) => {
    try {
      await api.put(`/inventory/endpoints/${endpointId}/classify`, {
        classification: newClass,
        recommendation: newClass === 'active' ? 'Re-authorized by security team' : 'Marked for deprecation'
      });
      fetchInventory();
    } catch (err) {
      alert('Failed to update: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            <span>API Inventory & Governance</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Agent 3 continuous classification: Active, Zombie (obsolete but accessible), and Shadow (undocumented) endpoints.
          </p>
        </div>

        <button
          onClick={triggerReclassify}
          disabled={refreshing}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white flex items-center gap-2 shadow-lg shadow-cyan-600/20 font-mono transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
          <span>{refreshing ? 'Evaluating...' : 'Run Agent 3 Classification'}</span>
        </button>
      </div>

      {/* Inventory Breakdown Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="cyber-card rounded-xl p-5 border-t-4 border-t-emerald-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs uppercase font-mono font-bold text-emerald-400">Active APIs</p>
              <h3 className="text-3xl font-bold font-mono text-white mt-1">{stats?.active_apis ?? 0}</h3>
              <p className="text-xs text-slate-400 mt-1">Legitimate endpoints in active business use</p>
            </div>
            <span className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-5 h-5" />
            </span>
          </div>
        </div>

        <div className="cyber-card rounded-xl p-5 border-t-4 border-t-amber-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs uppercase font-mono font-bold text-amber-400">Zombie APIs</p>
              <h3 className="text-3xl font-bold font-mono text-white mt-1">{stats?.zombie_apis ?? 0}</h3>
              <p className="text-xs text-slate-400 mt-1">Outdated / deprecated routes still reachable</p>
            </div>
            <span className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-5 h-5" />
            </span>
          </div>
        </div>

        <div className="cyber-card rounded-xl p-5 border-t-4 border-t-purple-500">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs uppercase font-mono font-bold text-purple-400">Shadow APIs</p>
              <h3 className="text-3xl font-bold font-mono text-white mt-1">{stats?.shadow_apis ?? 0}</h3>
              <p className="text-xs text-slate-400 mt-1">In-use routes missing from API documentation</p>
            </div>
            <span className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Layers className="w-5 h-5" />
            </span>
          </div>
        </div>
      </div>

      {/* Inventory & Recommendations Table */}
      <div className="cyber-card rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            API Inventory & Actionable Decommissioning Guidance
          </h3>
          <span className="text-xs text-slate-400 font-mono">Total Tracked: {endpoints.length}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px]">
              <tr>
                <th className="py-3 px-4">Method</th>
                <th className="py-3 px-4">Endpoint Path</th>
                <th className="py-3 px-4">Classification</th>
                <th className="py-3 px-4">Agent 3 Governance Recommendation</th>
                <th className="py-3 px-4 text-right">Adjust State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {endpoints.map((ep) => (
                <tr key={ep.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4">
                    <MethodBadge method={ep.method} />
                  </td>
                  <td className="py-3 px-4 font-mono font-medium text-slate-200">
                    {ep.path}
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={ep.classification} size="xs" />
                  </td>
                  <td className="py-3 px-4 text-slate-300 max-w-md">
                    {ep.recommendation ? (
                      <span className="text-amber-300/90 font-mono text-[11px] flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-400" />
                        <span>{ep.recommendation}</span>
                      </span>
                    ) : (
                      <span className="text-slate-400 font-mono text-[11px]">Regular CI/CD testing schedule active</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {ep.classification !== 'active' && (
                        <button
                          onClick={() => updateClassification(ep.id, 'active')}
                          className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-emerald-400 font-mono border border-slate-700"
                        >
                          Mark Active
                        </button>
                      )}
                      {ep.classification !== 'zombie' && (
                        <button
                          onClick={() => updateClassification(ep.id, 'zombie')}
                          className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-amber-400 font-mono border border-slate-700"
                        >
                          Mark Zombie
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

