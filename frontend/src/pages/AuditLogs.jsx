import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Terminal, RefreshCw, Filter } from 'lucide-react';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const res = await api.get('/audit/logs?limit=50');
      setLogs(res.data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Terminal className="w-5 h-5 text-cyan-400" />
            <span>Immutable Security Audit Trail</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Complete compliance logging of scans, verification decisions, policy approvals, and developer remediations.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 hover:text-white bg-slate-800 border border-slate-700 flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit Trail</span>
        </button>
      </div>

      <div className="cyber-card rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Resource</th>
                <th className="py-3 px-4">Resource ID</th>
                <th className="py-3 px-4">IP Origin</th>
                <th className="py-3 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/40 text-[11px]">
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-cyan-300">
                    {log.action}
                  </td>
                  <td className="py-3 px-4 uppercase text-slate-300">
                    {log.resource_type}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {log.resource_id || '-'}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-500">
                    {log.ip_address}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400 max-w-xs truncate">
                    {JSON.stringify(log.details_json || {})}
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
