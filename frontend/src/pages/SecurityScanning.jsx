import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import {
  Crosshair,
  Play,
  StopCircle,
  ShieldCheck,
  Cpu,
  AlertOctagon,
  Clock,
  Layers,
  ChevronRight,
  RefreshCw
} from 'lucide-react';

export const SecurityScanning = () => {
  const [scans, setScans] = useState([]);
  const [targets, setTargets] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState(1);
  const [selectedCategories, setSelectedCategories] = useState([
    'access_control',
    'business_logic',
    'authentication',
    'injection',
    'api_security'
  ]);
  const [rateLimit, setRateLimit] = useState(5.0);
  const [isScanning, setIsScanning] = useState(false);
  const [activeScanId, setActiveScanId] = useState(null);
  const [agentLogs, setAgentLogs] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const fetchScans = async () => {
    try {
      const [scansRes, targetsRes] = await Promise.all([
        api.get('/scans'),
        api.get('/targets')
      ]);
      setScans(scansRes.data);
      setTargets(targetsRes.data);
      if (targetsRes.data.length > 0 && !selectedTarget) {
        setSelectedTarget(targetsRes.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch scans:', err);
    }
  };

  const fetchLogs = async (scanId) => {
    try {
      const res = await api.get(`/scans/${scanId}/logs`);
      setAgentLogs(res.data);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    }
  };

  useEffect(() => {
    fetchScans();
  }, []);

  useEffect(() => {
    if (activeScanId) {
      fetchLogs(activeScanId);
      const interval = setInterval(() => fetchLogs(activeScanId), 3000);
      return () => clearInterval(interval);
    }
  }, [activeScanId]);

  const toggleCategory = (cat) => {
    if (selectedCategories.includes(cat)) {
      setSelectedCategories(selectedCategories.filter(c => c !== cat));
    } else {
      setSelectedCategories([...selectedCategories, cat]);
    }
  };

  const handleStartScan = async () => {
    try {
      setIsScanning(true);
      setShowModal(false);
      const res = await api.post('/scans', {
        target_id: selectedTarget,
        scan_name: `Automated Multi-Agent DAST Scan - ${new Date().toLocaleTimeString()}`,
        scan_type: 'full',
        selected_categories: selectedCategories,
        rate_limit_rps: rateLimit,
        auto_verify: true
      });
      setActiveScanId(res.data.id);
      fetchScans();
      fetchLogs(res.data.id);
    } catch (err) {
      alert('Failed to start scan: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsScanning(false);
    }
  };

  const handleStopScan = async (scanId) => {
    try {
      await api.post(`/scans/${scanId}/stop`);
      fetchScans();
      alert('Emergency scan stop initiated.');
    } catch (err) {
      alert('Stop error: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Crosshair className="w-5 h-5 text-cyan-400" />
            <span>Targeted Security Scanning Engine</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Safe, non-destructive autonomous multi-agent testing bounded by Agent 6 Safety & Policy controls.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          disabled={isScanning}
          className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-95 text-white flex items-center gap-2 shadow-lg shadow-cyan-500/25 font-mono"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>Configure & Launch Scan</span>
        </button>
      </div>

      {/* Active Scan Progress / Inspector */}
      {activeScanId && (
        <div className="cyber-card rounded-2xl p-6 border-cyan-500/30 glow-blue">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-cyan-400 animate-ping" />
              <div>
                <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
                  Active Scan #{activeScanId} Execution Stream
                </h3>
                <p className="text-xs text-slate-400 font-mono">
                  Multi-agent synchronization in progress
                </p>
              </div>
            </div>
            <button
              onClick={() => handleStopScan(activeScanId)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 flex items-center gap-1.5 font-mono"
            >
              <StopCircle className="w-4 h-4" />
              <span>Emergency Abort</span>
            </button>
          </div>

          {/* Logs Terminal */}
          <div className="bg-[#05070d] rounded-xl p-4 border border-slate-800 font-mono text-xs max-h-72 overflow-y-auto space-y-2">
            {agentLogs.length > 0 ? (
              agentLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-2 text-[11px] leading-relaxed">
                  <span className="text-slate-500 shrink-0">
                    [{new Date(log.created_at).toLocaleTimeString()}]
                  </span>
                  <span className="text-cyan-400 font-semibold shrink-0">
                    [{log.agent_name}]
                  </span>
                  <span className="text-slate-300">
                    {log.step_name}: {log.output_summary}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-slate-500">Initializing multi-agent graph...</p>
            )}
          </div>
        </div>
      )}

      {/* Scan History Table */}
      <div className="cyber-card rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            Security Scan Execution History
          </h3>
          <button onClick={fetchScans} className="text-slate-400 hover:text-white p-1">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px]">
              <tr>
                <th className="py-3 px-4">Scan ID</th>
                <th className="py-3 px-4">Scan Name</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Endpoints</th>
                <th className="py-3 px-4">Vulnerabilities</th>
                <th className="py-3 px-4">Triggered By</th>
                <th className="py-3 px-4">Started At</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {scans.length > 0 ? (
                scans.map((s) => (
                  <tr
                    key={s.id}
                    onClick={() => setActiveScanId(s.id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400">
                      #{s.id}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-200 max-w-xs truncate">
                      {s.scan_name}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={s.status} size="xs" />
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">
                      {s.tested_endpoints} / {s.total_endpoints}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold">
                      <span className={s.vulnerabilities_count > 0 ? 'text-rose-400' : 'text-emerald-400'}>
                        {s.vulnerabilities_count} Findings
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {s.triggered_by}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {s.start_time ? new Date(s.start_time).toLocaleTimeString() : 'Pending'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button className="text-cyan-400 hover:text-cyan-300 font-mono text-xs flex items-center gap-1 ml-auto">
                        <span>Logs</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-slate-500">
                    No scans recorded yet. Click "Configure & Launch Scan" to start.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Start Scan Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0e1424] border border-slate-700/80 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div>
              <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
                <Crosshair className="w-5 h-5 text-cyan-400" />
                <span>Launch Autonomous Multi-Agent Scan</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Select an approved target and test categories. Agent 4 will generate targeted precision test vectors.
              </p>
            </div>

            {/* Target Selection */}
            <div>
              <label className="text-xs font-mono text-slate-300 uppercase block mb-1.5">
                Approved Target
              </label>
              <select
                value={selectedTarget}
                onChange={(e) => setSelectedTarget(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              >
                {targets.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.target_url})
                  </option>
                ))}
              </select>
            </div>

            {/* Test Categories */}
            <div>
              <label className="text-xs font-mono text-slate-300 uppercase block mb-2">
                Targeted Test Categories
              </label>
              <div className="space-y-2">
                {[
                  { id: 'access_control', name: 'Access Control (Cross-Agency IDOR / BOLA)', desc: 'Validates tenant boundaries between Travel Agencies' },
                  { id: 'business_logic', name: 'Business Logic (Fare Manipulation & Duplicate Refunds)', desc: 'Validates pricing calculations and idempotency locks' },
                  { id: 'authentication', name: 'Authentication & Session Weaknesses', desc: 'Checks token verification and unauthorized legacy access' },
                  { id: 'api_security', name: 'API Security (Zombie & Shadow API Exposure)', desc: 'Audits unmaintained endpoints and excessive PII leakage' },
                ].map((item) => (
                  <label
                    key={item.id}
                    className="flex items-start gap-3 p-3 rounded-lg bg-slate-900/60 border border-slate-800 cursor-pointer hover:border-slate-700"
                  >
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(item.id)}
                      onChange={() => toggleCategory(item.id)}
                      className="mt-1 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0"
                    />
                    <div>
                      <p className="text-xs font-semibold text-slate-200">{item.name}</p>
                      <p className="text-[11px] text-slate-400">{item.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Safety Rate Limit */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-mono text-slate-300 uppercase">
                  Safety Rate Limit: {rateLimit} RPS
                </label>
                <span className="text-[11px] text-emerald-400 font-mono">Agent 6 Policy Safe</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={rateLimit}
                onChange={(e) => setRateLimit(Number(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            {/* Modal Actions */}
            <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-300 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleStartScan}
                className="px-5 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white font-mono shadow-lg shadow-cyan-600/20"
              >
                Begin Scan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

