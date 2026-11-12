import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Compass,
  Layers,
  ShieldAlert,
  Bug,
  Cpu,
  FileBarChart,
  Terminal,
  Crosshair,
  ShieldCheck,
  Server
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/discovery', label: 'API Discovery', icon: Compass },
  { path: '/inventory', label: 'API Inventory', icon: Layers },
  { path: '/scans', label: 'Security Scans', icon: Crosshair },
  { path: '/vulnerabilities', label: 'Vulnerabilities', icon: Bug },
  { path: '/agents', label: 'Agent Activity', icon: Cpu, badge: '10' },
  { path: '/staging-testbed', label: 'Staging App Testbed', icon: Server, highlight: true },
  { path: '/reports', label: 'Reports & Analytics', icon: FileBarChart },
  { path: '/targets', label: 'Authorized Targets', icon: ShieldCheck },
  { path: '/audit', label: 'Audit Trail', icon: Terminal },
];

export const Sidebar = () => {
  return (
    <aside className="w-64 bg-[#0a0e17] border-r border-slate-800/80 flex flex-col shrink-0 min-h-screen">
      {/* Brand logo */}
      <div className="p-6 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-base text-white tracking-wide font-mono flex items-center gap-1.5">
            SENTINEL<span className="text-cyan-400">AI</span>
          </h1>
          <p className="text-[10px] text-cyan-400 font-mono tracking-wider uppercase">DAST Multi-Agent Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1 flex-1 overflow-y-auto">
        <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2 font-mono">
          Security Operations
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                    : item.highlight
                    ? 'text-amber-400 hover:bg-amber-500/10 hover:text-amber-300 border border-amber-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.2 bg-cyan-500/20 text-cyan-300 font-mono text-[10px] rounded-full border border-cyan-500/30">
                  {item.badge}
                </span>
              )}
              {item.highlight && (
                <span className="px-1.5 py-0.2 bg-amber-500/20 text-amber-300 font-mono text-[9px] rounded uppercase font-bold">
                  Demo
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Safety Policy Box */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 text-xs">
          <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Agent 6 Safety Guard</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Strict allowlist only • 5 RPS rate limit • Synthetic staging boundary enforced.
          </p>
        </div>
      </div>
    </aside>
  );
};
