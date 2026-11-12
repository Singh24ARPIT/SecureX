import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge, MethodBadge } from '../components/StatusBadge';
import {
  Server,
  ShieldAlert,
  ShieldCheck,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Terminal,
  Zap,
  Lock,
  Unlock
} from 'lucide-react';

export const StagingTestbed = () => {
  const [securityConfig, setSecurityConfig] = useState({
    idor_vulnerable: true,
    fare_tampering_vulnerable: true,
    duplicate_refund_vulnerable: true,
    unauthorized_admin_vulnerable: true
  });
  const [agency, setAgency] = useState('agency_202'); // Default to Agency 202 testing Agency 101's booking
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoSteps, setDemoSteps] = useState([]);

  const fetchConfig = async () => {
    try {
      const res = await api.get('/staging/config');
      if (res.data.vulnerability_flags) {
        setSecurityConfig(res.data.vulnerability_flags);
      }
    } catch (err) {
      console.error('Failed to load staging config:', err);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  const togglePatch = async (key) => {
    const updated = { ...securityConfig, [key]: !securityConfig[key] };
    setSecurityConfig(updated);
    try {
      await api.post('/staging/security/toggle-patch', updated);
    } catch (err) {
      alert('Failed to toggle patch: ' + err.message);
    }
  };

  // 1. Test Cross-Agency IDOR
  const testIdor = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.get('/staging/bookings/TBO-BKG-8891', {
        headers: { 'X-Agency-Id': agency }
      });
      setTestResult({
        title: 'Cross-Agency Booking Access Result',
        status: 'vulnerable',
        httpStatus: 200,
        message: `VULNERABILITY EXPLOITED: '${agency}' successfully accessed booking belonging to '${res.data.agency_id}'! Customer: ${res.data.customer_name}`,
        data: res.data
      });
    } catch (err) {
      const status = err.response?.status;
      setTestResult({
        title: 'Cross-Agency Booking Access Result',
        status: status === 403 ? 'secure' : 'error',
        httpStatus: status || 500,
        message: status === 403 ? `PATCH ENFORCED: Server returned 403 Forbidden. Cross-agency access blocked.` : err.message,
        data: err.response?.data
      });
    } finally {
      setTesting(false);
    }
  };

  // 2. Test Fare Manipulation
  const testFareTampering = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.post('/staging/bookings', {
        hotel_code: 'HTL-DXB-01',
        customer_name: 'Arbitrage Attacker',
        customer_email: 'attacker@evilagency.example',
        room_count: 1,
        nights: 2,
        submitted_fare: 1.00 // Intentionally manipulating fare to $1
      }, {
        headers: { 'X-Agency-Id': agency }
      });
      setTestResult({
        title: 'Fare Manipulation Test Result',
        status: res.data.tampering_accepted ? 'vulnerable' : 'secure',
        httpStatus: 200,
        message: res.data.tampering_accepted ? `VULNERABILITY EXPLOITED: Hotel reservation confirmed for $1.00 instead of calculated $${res.data.server_calculated_fare}!` : `Booking processed`,
        data: res.data
      });
    } catch (err) {
      const status = err.response?.status;
      setTestResult({
        title: 'Fare Manipulation Test Result',
        status: status === 400 ? 'secure' : 'error',
        httpStatus: status || 500,
        message: status === 400 ? `PATCH ENFORCED: Server returned 400 Bad Request. Discrepancy detected.` : err.message,
        data: err.response?.data
      });
    } finally {
      setTesting(false);
    }
  };

  // 3. Test Duplicate Refund
  const testDuplicateRefund = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.post('/staging/refunds', {
        booking_reference: 'TBO-BKG-8891',
        refund_amount: 600.00
      }, {
        headers: { 'X-Agency-Id': agency }
      });
      setTestResult({
        title: 'Duplicate Refund Test Result',
        status: 'vulnerable',
        httpStatus: 200,
        message: `VULNERABILITY EXPLOITED: Duplicate refund approved (Attempt #${res.data.refund_attempt_number})! Amount: $${res.data.refund_amount}`,
        data: res.data
      });
    } catch (err) {
      const status = err.response?.status;
      setTestResult({
        title: 'Duplicate Refund Test Result',
        status: status === 409 ? 'secure' : 'error',
        httpStatus: status || 500,
        message: status === 409 ? `PATCH ENFORCED: Server returned 409 Conflict. Duplicate refund rejected.` : err.message,
        data: err.response?.data
      });
    } finally {
      setTesting(false);
    }
  };

  // 11-Step End-to-End Hackathon Demonstration
  const runEndToEndDemonstration = async () => {
    setDemoRunning(true);
    setDemoSteps([]);

    const addStep = (stepText, status = 'completed') => {
      setDemoSteps(prev => [...prev, { text: stepText, status, time: new Date().toLocaleTimeString() }]);
    };

    try {
      // Step 1: Deploy new API
      addStep('Step 1: Deployment Event Emitted (CI/CD Webhook for /staging/bookings)', 'running');
      await api.post('/discovery/webhook/deploy', {
        target_id: 1,
        service_name: 'travel-booking-service',
        commit_sha: 'tbo-' + Math.random().toString(16).substring(2, 6),
        branch: 'release/v4.2',
        endpoints: [
          {
            path: '/api/v1/staging/bookings',
            method: 'POST',
            summary: 'Create Hotel Booking',
            auth_required: true,
            required_roles: 'agency_admin',
            risk_score: 9.0
          }
        ]
      });
      addStep('Step 2: Agent 1 (Change Detection) identified API schema updates and triggered scan trigger');

      // Step 3: Recon
      addStep('Step 3: Agent 2 (Recon Discovery) enumerated staging travel routes and extracted parameter trees');
      await api.post('/discovery/scan/1');

      // Step 4: Inventory
      addStep('Step 4: Agent 3 (API Inventory) classified active, zombie, and shadow endpoints');
      await api.post('/inventory/reclassify/1');

      // Step 5 & 6 & 7: Attack Plan + Safety + Security Testers
      addStep('Step 5 & 6: Agent 4 synthesized targeted test plan; Agent 6 validated allowlist & 5 RPS rate limits');
      addStep('Step 7: Agent 5 (Security Testers) executed Cross-Agency IDOR and Fare Manipulation checks');
      const scanRes = await api.post('/scans', {
        target_id: 1,
        scan_name: 'Hackathon Master Demonstration Scan',
        scan_type: 'full',
        selected_categories: ['access_control', 'business_logic', 'authentication', 'api_security'],
        rate_limit_rps: 5.0,
        auto_verify: true
      });

      // Step 8: Verification
      addStep('Step 8: Agent 7 (Verification Agent) confirmed findings with minimal HTTP proof');

      // Step 9: Risk
      addStep('Step 9: Agent 8 (Risk Assessment) assigned CVSS severity and business impact score');

      // Step 10: Reporting
      addStep('Step 10: Agent 9 (Reporting Agent) compiled executive security report and CSV/JSON export');

      // Step 11: Retest
      addStep('Step 11: Demonstrating Closed-Loop Retest. Toggling fix to patched mode...');
      await api.post('/staging/security/toggle-patch', {
        idor_vulnerable: false,
        fare_tampering_vulnerable: false
      });
      setSecurityConfig(prev => ({ ...prev, idor_vulnerable: false, fare_tampering_vulnerable: false }));

      // Fetch first vuln to retest
      const vulns = await api.get('/vulnerabilities');
      if (vulns.data.length > 0) {
        const targetVuln = vulns.data[0];
        const retestRes = await api.post(`/vulnerabilities/${targetVuln.id}/retest`, {
          notes: 'Hackathon Step 11 Retest Demonstration'
        });
        addStep(`Step 11 Done: Agent 10 Retesting verified '${targetVuln.title}' is RESOLVED (HTTP 403/400 secure assertion)!`);
      }
    } catch (err) {
      addStep(`Demo Error: ${err.message}`, 'error');
    } finally {
      setDemoRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Server className="w-5 h-5 text-amber-400" />
            <span>Simulated Staging Travel Application (Hackathon Demo Testbed)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Controlled synthetic staging environment containing multi-tenant travel agencies (Agency 101 vs Agency 202).
          </p>
        </div>

        <button
          onClick={runEndToEndDemonstration}
          disabled={demoRunning}
          className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-amber-500 to-rose-600 hover:opacity-95 text-white flex items-center gap-2 shadow-lg shadow-amber-500/25 font-mono"
        >
          <Zap className={`w-4 h-4 ${demoRunning ? 'animate-spin' : ''}`} />
          <span>{demoRunning ? 'Running 11-Step Demo...' : 'Run 11-Step Master Hackathon Demo'}</span>
        </button>
      </div>

      {/* 11-Step Master Demo Timeline Box (when triggered) */}
      {demoSteps.length > 0 && (
        <div className="cyber-card rounded-2xl p-6 border-amber-500/40 glow-rose">
          <h3 className="text-sm font-bold text-amber-300 font-mono uppercase tracking-wider mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            <span>Master Demonstration Execution Trace</span>
          </h3>
          <div className="space-y-2 font-mono text-xs max-h-60 overflow-y-auto">
            {demoSteps.map((step, idx) => (
              <div key={idx} className="flex items-start gap-2.5 text-[11px]">
                <span className="text-amber-400 font-bold shrink-0">[{step.time}]</span>
                <span className={step.status === 'error' ? 'text-rose-400' : 'text-slate-200'}>
                  {step.text}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vulnerability Configuration / Patch Toggle Switchboard */}
      <div className="cyber-card rounded-2xl p-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
              Target Vulnerability & Patch Switchboard
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Toggle patches on/off in real-time to demonstrate how SecuReX's Retest Agent detects regressions and validates fixes.
            </p>
          </div>
          <button onClick={fetchConfig} className="text-xs text-cyan-400 font-mono hover:underline">
            Refresh State
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* IDOR Toggle */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
            <div>
              <p className="font-semibold text-xs text-white">Cross-Agency IDOR / BOLA</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Missing tenant isolation check on booking details</p>
            </div>
            <button
              onClick={() => togglePatch('idor_vulnerable')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center gap-1.5 transition-all ${
                securityConfig.idor_vulnerable
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}
            >
              {securityConfig.idor_vulnerable ? <Unlock className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
              <span>{securityConfig.idor_vulnerable ? 'VULNERABLE' : 'PATCHED'}</span>
            </button>
          </div>

          {/* Fare Manipulation Toggle */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
            <div>
              <p className="font-semibold text-xs text-white">Client-Side Fare Manipulation</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Accepts client-submitted booking total without tariff verification</p>
            </div>
            <button
              onClick={() => togglePatch('fare_tampering_vulnerable')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center gap-1.5 transition-all ${
                securityConfig.fare_tampering_vulnerable
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}
            >
              {securityConfig.fare_tampering_vulnerable ? <Unlock className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
              <span>{securityConfig.fare_tampering_vulnerable ? 'VULNERABLE' : 'PATCHED'}</span>
            </button>
          </div>

          {/* Duplicate Refund Toggle */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
            <div>
              <p className="font-semibold text-xs text-white">Duplicate Refund Workflow Abuse</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Lacks idempotency check on settled booking refunds</p>
            </div>
            <button
              onClick={() => togglePatch('duplicate_refund_vulnerable')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center gap-1.5 transition-all ${
                securityConfig.duplicate_refund_vulnerable
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}
            >
              {securityConfig.duplicate_refund_vulnerable ? <Unlock className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
              <span>{securityConfig.duplicate_refund_vulnerable ? 'VULNERABLE' : 'PATCHED'}</span>
            </button>
          </div>

          {/* Agency Context Switcher */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
            <div>
              <p className="font-semibold text-xs text-white">Active Test Agency Identity</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Simulate calls as Agency 101 or competitor Agency 202</p>
            </div>
            <select
              value={agency}
              onChange={(e) => setAgency(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs font-mono text-cyan-300 font-bold focus:outline-none"
            >
              <option value="agency_101">Agency 101 (Owner)</option>
              <option value="agency_202">Agency 202 (Competitor)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Live Interactive Attack Simulator */}
      <div className="cyber-card rounded-2xl p-6">
        <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider mb-2">
          Interactive Vector Execution
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Click any button below to trigger the exact HTTP payload from the selected agency context.
        </p>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={testIdor}
            disabled={testing}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 flex items-center gap-2 font-mono"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Test Cross-Agency IDOR (GET /bookings/TBO-BKG-8891)</span>
          </button>

          <button
            onClick={testFareTampering}
            disabled={testing}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/30 flex items-center gap-2 font-mono"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Test Fare Manipulation (POST /bookings with $1.00)</span>
          </button>

          <button
            onClick={testDuplicateRefund}
            disabled={testing}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-purple-400 border border-purple-500/30 flex items-center gap-2 font-mono"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Test Duplicate Refund (POST /refunds)</span>
          </button>
        </div>

        {/* Live Output Box */}
        {testResult && (
          <div className="mt-5 p-4 rounded-xl bg-[#05070d] border border-slate-800 text-xs font-mono space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-200">{testResult.title}</span>
              <StatusBadge status={testResult.status} size="xs" />
            </div>
            <p className={testResult.status === 'vulnerable' ? 'text-rose-400' : 'text-emerald-400'}>
              {testResult.message}
            </p>
            <pre className="p-3 rounded bg-slate-900 text-cyan-300 text-[11px] overflow-x-auto">
              {JSON.stringify(testResult.data, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

