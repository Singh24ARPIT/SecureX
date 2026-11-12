import React from 'react';

export const StatusBadge = ({ status, size = 'sm' }) => {
  const s = (status || '').toLowerCase();
  
  let styles = 'bg-slate-800 text-slate-300 border-slate-700';

  if (['critical', 'failed', 'alert', 'error'].includes(s)) {
    styles = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
  } else if (['high', 'zombie', 'warning'].includes(s)) {
    styles = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
  } else if (['medium', 'shadow'].includes(s)) {
    styles = 'bg-purple-500/15 text-purple-400 border-purple-500/30';
  } else if (['low', 'info'].includes(s)) {
    styles = 'bg-blue-500/15 text-blue-400 border-blue-500/30';
  } else if (['active', 'passed', 'completed', 'resolved', 'verified', 'healthy'].includes(s)) {
    styles = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
  } else if (['running', 'pending', 'retesting'].includes(s)) {
    styles = 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30 animate-pulse';
  }

  const sizeClass = size === 'xs' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${sizeClass} ${styles} uppercase tracking-wider`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {status}
    </span>
  );
};

export const MethodBadge = ({ method }) => {
  const m = (method || '').toUpperCase();
  const colors = {
    GET: 'bg-blue-500/20 text-blue-400 border-blue-500/40',
    POST: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
    PUT: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
    PATCH: 'bg-purple-500/20 text-purple-400 border-purple-500/40',
    DELETE: 'bg-rose-500/20 text-rose-400 border-rose-500/40',
  };

  return (
    <span className={`px-2 py-0.5 font-mono text-xs font-bold rounded border ${colors[m] || 'bg-slate-700 text-slate-300'}`}>
      {m}
    </span>
  );
};

