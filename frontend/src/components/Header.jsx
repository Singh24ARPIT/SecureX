import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, LogOut, Activity, Play, Bell, Radio } from 'lucide-react';
import api from '../api/client';

export const Header = ({ onScanTriggered }) => {
  const { user, logout } = useAuth();
  const [deploying, setDeploying] = useState(false);

  const simulateDeploy = async () => {
    try {
      setDeploying(true);
      await api.post('/discovery/webhook/deploy', {
        target_id: 1,
        service_name: 'travel-booking-service',
        commit_sha: 'c8f' + Math.random().toString(16).substring(2, 7),
        branch: 'release/v4.2-staging',
        triggered_by: 'CI/CD Webhook (GitHub Actions)',
        event_type: 'api_deploy',
        endpoints: [
          {
            path: '/api/v1/staging/bookings',
            method: 'POST',
            summary: 'Create Hotel Booking (Updated)',
            auth_required: true,
            required_roles: 'agency_admin',
            risk_score: 9.0
          }
        ]
      });
      alert('Simulated CI/CD Deployment Webhook processed! Agent 1 (Change Detection) detected API drift.');
      if (onScanTriggered) onScanTriggered();
    } catch (err) {
      alert('Error triggering deploy event: ' + err.message);
    } finally {
      setDeploying(false);
    }
  };

  return (
    <header className="h-16 bg-[#0a0e17]/80 backdrop-blur-md border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        {/* Status Pill */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>10 AGENTS ONLINE</span>
        </div>

        <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 font-mono">
          <span className="text-slate-600">|</span>
          <span>Target:</span>
          <span className="text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/50">
            TBO Staging API Cluster
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Quick Webhook Trigger for Demonstrating Agent 1 */}
        <button
          onClick={simulateDeploy}
          disabled={deploying}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 transition-all font-mono"
        >
          <Radio className={`w-3.5 h-3.5 ${deploying ? 'animate-spin' : ''}`} />
          <span>{deploying ? 'Emitting...' : 'Simulate Deploy Webhook'}</span>
        </button>

        {/* User Badge */}
        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
          <div className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center text-xs font-bold font-mono">
            {user?.username ? user.username[0].toUpperCase() : 'U'}
          </div>
          <div className="text-left">
            <p className="text-xs font-semibold text-slate-200">{user?.full_name || user?.username}</p>
            <p className="text-[10px] text-cyan-400 font-mono uppercase">{user?.role?.replace('_', ' ')}</p>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={logout}
          title="Sign out"
          className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 transition-colors"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
