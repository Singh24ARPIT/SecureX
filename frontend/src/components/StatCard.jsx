import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'blue', trend }) => {
  const colorMap = {
    blue: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/5',
    rose: 'text-rose-400 border-rose-500/20 bg-rose-500/5',
    amber: 'text-amber-400 border-amber-500/20 bg-amber-500/5',
    emerald: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5',
    purple: 'text-purple-400 border-purple-500/20 bg-purple-500/5',
  };

  return (
    <div className="cyber-card rounded-xl p-5 relative overflow-hidden transition-all duration-200 hover:-translate-y-0.5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-slate-100">{value}</span>
            {trend && (
              <span className={`text-xs font-semibold ${trend.startsWith('+') ? 'text-rose-400' : 'text-emerald-400'}`}>
                {trend}
              </span>
            )}
          </div>
          {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg border ${colorMap[color] || colorMap.blue}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
      <div className={`absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-${color}-500/40 to-transparent`} />
    </div>
  );
};

