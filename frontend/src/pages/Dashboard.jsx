import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import {
  Compass,
  Layers,
  ShieldAlert,
  Bug,
  Activity,
  HeartPulse,
  Play,
  ArrowRight,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  AreaChart,
  Area
} from 'recharts';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState(null);
  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [overviewRes, trendsRes, logsRes] = await Promise.all([
        api.get('/dashboard/overview'),
        api.get('/dashboard/trends'),
        api.get('/agents/status')
      ]);
      setStats(overviewRes.data);
      setTrends(trendsRes.data);
      setRecentLogs(logsRes.data.recent_activity || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const severityData = stats ? [
    { name: 'Critical', value: stats.critical_vulnerabilities, color: '#f43f5e' },
    { name: 'High', value: stats.high_vulnerabilities, color: '#f59e0b' },
    { name: 'Medium', value: stats.medium_vulnerabilities, color: '#a855f7' },
    { name: 'Low', value: stats.low_vulnerabilities, color: '#38bdf8' },
  ].filter(d => d.value > 0) : [];

  const categoryData = trends?.by_category ? Object.entries(trends.by_category).map(([k, v]) => ({
    name: k.replace('_', ' ').toUpperCase(),
    count: v
  })) : [];

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Actions */}
      <div className="cyber-card rounded-2xl p-6 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase">
              VOYAGEHACK 4.0 | TBO Security Hackathon
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            SentinelAI Autonomous Real-Time DAST
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Autonomous multi-agent orchestration for dynamic API change detection, deep business logic testing, cross-agency IDOR analysis, and deterministic retesting.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/staging-testbed')}
            className="px-4 py-2.5 rounded-xl font-medium text-xs bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 transition-all flex items-center gap-2"
          >
            <span>Open Staging Testbed</span>
            <ArrowRight className="w-4 h-4 text-slate-400" />
          </button>
          <button
            onClick={() => navigate('/scans')}
            className="px-4 py-2.5 rounded-xl font-medium text-xs bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/25 hover:opacity-95 transition-all flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            <span>Launch Security Scan</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Security Health Score"
          value={`${stats?.security_health_score ?? 100}%`}
          subtitle="Dynamic posture index"
          icon={HeartPulse}
          color={stats?.security_health_score > 70 ? 'emerald' : 'rose'}
        />
        <StatCard
          title="Total Discovered APIs"
          value={stats?.total_apis ?? 0}
          subtitle={`${stats?.active_apis ?? 0} Active • ${stats?.zombie_apis ?? 0} Zombie • ${stats?.shadow_apis ?? 0} Shadow`}
          icon={Compass}
          color="blue"
        />
        <StatCard
          title="Critical Vulnerabilities"
          value={stats?.critical_vulnerabilities ?? 0}
          subtitle="IDOR & Fare Manipulation Flaws"
          icon={ShieldAlert}
          color="rose"
        />
        <StatCard
          title="Verified Findings"
          value={stats?.verified_vulnerabilities ?? 0}
          subtitle="False-positive filtered (Agent 7)"
          icon={ShieldCheck}
          color="emerald"
        />
      </div>

      {/* Secondary Metric Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="cyber-card rounded-xl p-4 border-l-4 border-l-rose-500">
          <p className="text-xs text-slate-400 uppercase font-mono">Zombie APIs</p>
          <p className="text-xl font-bold font-mono text-slate-100 mt-1">{stats?.zombie_apis ?? 0}</p>
          <p className="text-[11px] text-amber-400 mt-0.5">Deprecated reachable routes</p>
        </div>
        <div className="cyber-card rounded-xl p-4 border-l-4 border-l-purple-500">
          <p className="text-xs text-slate-400 uppercase font-mono">Shadow APIs</p>
          <p className="text-xl font-bold font-mono text-slate-100 mt-1">{stats?.shadow_apis ?? 0}</p>
          <p className="text-[11px] text-purple-400 mt-0.5">Undocumented endpoints</p>
        </div>
        <div className="cyber-card rounded-xl p-4 border-l-4 border-l-cyan-500">
          <p className="text-xs text-slate-400 uppercase font-mono">False-Positive Rate</p>
          <p className="text-xl font-bold font-mono text-slate-100 mt-1">{trends?.false_positive_rate ?? 0}%</p>
          <p className="text-[11px] text-emerald-400 mt-0.5">Filtered by Verification Agent</p>
        </div>
        <div className="cyber-card rounded-xl p-4 border-l-4 border-l-emerald-500">
          <p className="text-xs text-slate-400 uppercase font-mono">Remediation Rate</p>
          <p className="text-xl font-bold font-mono text-slate-100 mt-1">{trends?.remediation_rate ?? 0}%</p>
          <p className="text-[11px] text-cyan-400 mt-0.5">Validated by Retest Agent</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Severity Breakdown Pie */}
        <div className="cyber-card rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
              Vulnerability Severity
            </h3>
            <span className="text-xs text-slate-400 font-mono">Total: {stats?.total_vulnerabilities ?? 0}</span>
          </div>
          {severityData.length > 0 ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-3 text-xs mt-2">
                {severityData.map((item) => (
                  <div key={item.name} className="flex items-center gap-1.5 font-mono">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-400">{item.name}:</span>
                    <span className="font-bold text-slate-200">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-56 flex flex-col items-center justify-center text-slate-500 text-xs">
              <ShieldCheck className="w-10 h-10 text-emerald-500/40 mb-2" />
              <span>No vulnerabilities recorded. Run a scan to test target.</span>
            </div>
          )}
        </div>

        {/* Category Distribution Bar Chart */}
        <div className="cyber-card rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
              Findings By Test Category
            </h3>
          </div>
          {categoryData.length > 0 ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                  <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-56 flex items-center justify-center text-slate-500 text-xs">
              Waiting for initial scan execution...
            </div>
          )}
        </div>

        {/* 7-Day Trend Area Chart */}
        <div className="cyber-card rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
              Detection vs Remediation Trend
            </h3>
          </div>
          {trends?.trends ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends.trends}>
                  <defs>
                    <linearGradient id="colorDetected" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="day" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                  <Area type="monotone" dataKey="detected" stroke="#f43f5e" fillOpacity={1} fill="url(#colorDetected)" />
                  <Area type="monotone" dataKey="resolved" stroke="#10b981" fillOpacity={1} fill="url(#colorResolved)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : null}
        </div>
      </div>

      {/* Live Agent Activity Feed */}
      <div className="cyber-card rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
              Live Agent Execution Stream
            </h3>
          </div>
          <button
            onClick={() => navigate('/agents')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1"
          >
            <span>View All 10 Agents</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="divide-y divide-slate-800/80">
          {recentLogs.length > 0 ? (
            recentLogs.slice(0, 5).map((log) => (
              <div key={log.id} className="py-3 flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-slate-200">{log.agent_name}</span>
                      <span className="text-[11px] text-slate-400 font-mono">› {log.step_name}</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 font-mono text-[11px]">
                      {log.output_summary}
                    </p>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <StatusBadge status={log.status} size="xs" />
                  <p className="text-[10px] text-slate-500 font-mono mt-1">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs">
              No recent agent executions. Launch a scan to observe real-time agent coordination.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

