import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import {
  Cpu,
  RefreshCw,
  Terminal,
  Activity,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  Zap,
  Clock
} from 'lucide-react';

export const AgentActivity = () => {
  const [agentData, setAgentData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAgentStatus = async () => {
    try {
      setLoading(true);
      const [statusRes, logsRes] = await Promise.all([
        api.get('/agents/status'),
        api.get('/agents/logs?limit=40')
      ]);
      setAgentData(statusRes.data);
      setLogs(logsRes.data);
    } catch (err) {
      console.error('Failed to load agent status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgentStatus();
    const interval = setInterval(fetchAgentStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span>Agent Activity Center (10 Autonomous Agents)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time status, assigned capabilities, and coordinated multi-agent testing timeline.
          </p>
        </div>

        <button
          onClick={fetchAgentStatus}
          className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:text-white flex items-center gap-2 font-mono border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Sync Agent Roster</span>
        </button>
      </div>

      {/* 10 Agents Matrix Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agentData?.agents?.map((agent, idx) => (
          <div key={agent.id} className="cyber-card rounded-xl p-5 relative overflow-hidden flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  AGENT {idx + 1}
                </span>
                <StatusBadge status={agent.status} size="xs" />
              </div>

              <h3 className="text-sm font-bold text-white">{agent.name}</h3>
              <p className="text-[11px] text-cyan-400/90 font-mono mt-0.5">{agent.type}</p>

              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                {agent.assigned_task}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] font-mono">
              <div className="flex justify-between text-slate-400">
                <span>Recent Step:</span>
                <span className="text-slate-200 truncate max-w-[160px] text-right">
                  {agent.last_step}
                </span>
              </div>
              <div className="flex justify-between text-slate-400 mt-1">
                <span>Last Synchronized:</span>
                <span className="text-cyan-400">
                  {agent.last_active ? new Date(agent.last_active).toLocaleTimeString() : 'Ready'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Global Agent Execution Log Stream */}
      <div className="cyber-card rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Coordinated Multi-Agent Execution Stream
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Showing {logs.length} logged turns</span>
        </div>

        <div className="bg-[#05070d] rounded-xl p-4 border border-slate-800 max-h-96 overflow-y-auto space-y-2.5 font-mono text-xs">
          {logs.length > 0 ? (
            logs.map((log) => (
              <div key={log.id} className="p-2.5 rounded bg-slate-900/40 border border-slate-800/60 flex items-start justify-between gap-4">
                <div className="flex items-start gap-2.5">
                  <span className="text-slate-500 text-[10px] shrink-0 mt-0.5">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-cyan-400">{log.agent_name}</span>
                      <span className="text-slate-400 text-[11px]">› {log.step_name}</span>
                    </div>
                    {log.input_summary && (
                      <p className="text-[11px] text-slate-400 mt-1">
                        Input: {log.input_summary}
                      </p>
                    )}
                    <p className="text-[11px] text-slate-200 mt-0.5 font-sans">
                      Result: {log.output_summary}
                    </p>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <StatusBadge status={log.status} size="xs" />
                  {log.execution_duration_ms > 0 && (
                    <p className="text-[10px] text-slate-500 mt-1 font-mono">
                      {log.execution_duration_ms.toFixed(0)} ms
                    </p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p className="text-slate-500">No agent actions recorded. Run a scan to see the agent coordination trace.</p>
          )}
        </div>
      </div>
    </div>
  );
};

