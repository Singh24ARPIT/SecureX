import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { ShieldCheck, Plus, CheckCircle2, ShieldAlert, Server } from 'lucide-react';

export const TargetManagement = () => {
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTargets = async () => {
    try {
      setLoading(true);
      const res = await api.get('/targets');
      setTargets(res.data);
    } catch (err) {
      console.error('Failed to load targets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTargets();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>Authorized Target Scope & Policy Bounds</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Agent 6 strictly enforces that only approved targets in authorized environments receive test requests.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {targets.map((target) => (
          <div key={target.id} className="cyber-card rounded-2xl p-6 border-emerald-500/20">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded border border-emerald-500/30 uppercase">
                {target.environment} Environment
              </span>
              <StatusBadge status={target.is_approved ? 'approved' : 'pending'} size="xs" />
            </div>

            <h3 className="text-base font-bold text-white">{target.name}</h3>
            <p className="text-xs font-mono text-cyan-300 mt-1 break-all">{target.target_url}</p>

            <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5 text-xs font-mono text-slate-400">
              <div className="flex justify-between">
                <span>Rate Limit Constraint:</span>
                <span className="text-slate-200">{target.rate_limit_rps} RPS</span>
              </div>
              <div className="flex justify-between">
                <span>Approved By:</span>
                <span className="text-slate-200">{target.approved_by}</span>
              </div>
              <div className="flex justify-between">
                <span>Health Monitoring:</span>
                <span className="text-emerald-400 font-bold uppercase">{target.health_status}</span>
              </div>
            </div>

            {target.approval_notes && (
              <p className="text-[11px] text-slate-400 mt-3 p-2.5 rounded bg-slate-900 border border-slate-800">
                {target.approval_notes}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
