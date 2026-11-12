import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import {
  Bug,
  Filter,
  CheckCircle2,
  RefreshCw,
  AlertTriangle,
  ShieldAlert,
  FileCheck,
  ChevronRight,
  X,
  ExternalLink,
  Code
} from 'lucide-react';

export const Vulnerabilities = () => {
  const [vulns, setVulns] = useState([]);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [selectedVuln, setSelectedVuln] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState(false);
  const [remediationModal, setRemediationModal] = useState(false);
  const [patchNotes, setPatchNotes] = useState('');

  const fetchVulns = async () => {
    try {
      setLoading(true);
      const params = {};
      if (severityFilter) params.severity = severityFilter;
      if (statusFilter) params.status = statusFilter;
      if (search) params.search = search;

      const res = await api.get('/vulnerabilities', { params });
      setVulns(res.data);
      if (selectedVuln) {
        const refreshed = res.data.find(v => v.id === selectedVuln.id);
        if (refreshed) setSelectedVuln(refreshed);
      }
    } catch (err) {
      console.error('Failed to load vulnerabilities:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVulns();
  }, [severityFilter, statusFilter, search]);

  const handleVerify = async (vulnId) => {
    try {
      setActionInProgress(true);
      const res = await api.post(`/vulnerabilities/${vulnId}/verify`);
      alert(`Agent 7 Verification Completed: Status is now '${res.data.status.toUpperCase()}'. Notes: ${res.data.verification_notes}`);
      fetchVulns();
    } catch (err) {
      alert('Verification error: ' + err.message);
    } finally {
      setActionInProgress(false);
    }
  };

  const handleRemediate = async () => {
    try {
      setActionInProgress(true);
      await api.post(`/vulnerabilities/${selectedVuln.id}/remediate`, {
        action_taken: 'Code patch committed in release/v4.2-staging',
        patch_details: patchNotes || 'Enforced server-side validation and multi-tenant authorization filter.',
        developer_notes: 'Marked fixed by developer. Awaiting Agent 10 Retesting.'
      });
      setRemediationModal(false);
      setPatchNotes('');
      alert('Remediation recorded! Vulnerability marked as "Remediated". You can now run Agent 10 Retest.');
      fetchVulns();
    } catch (err) {
      alert('Remediation logging failed: ' + err.message);
    } finally {
      setActionInProgress(false);
    }
  };

  const handleRetest = async (vulnId) => {
    try {
      setActionInProgress(true);
      const res = await api.post(`/vulnerabilities/${vulnId}/retest`, {
        notes: 'Automated post-patch regression test'
      });
      if (res.data.is_resolved) {
        alert(`AGENT 10 RETEST PASSED: Vulnerability successfully resolved! Secure assertion validated.`);
      } else {
        alert(`AGENT 10 RETEST FAILED: Flaw still reproduces on target! Target remains vulnerable.`);
      }
      fetchVulns();
    } catch (err) {
      alert('Retest error: ' + err.message);
    } finally {
      setActionInProgress(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bug className="w-5 h-5 text-rose-400" />
            <span>Vulnerability Management & Verification</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic verification (Agent 7), business risk scoring (Agent 8), and closed-loop regression retesting (Agent 10).
          </p>
        </div>

        <button
          onClick={fetchVulns}
          className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:text-white flex items-center gap-2 font-mono border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Findings</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="cyber-card rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <input
          type="text"
          placeholder="Filter by vulnerability title or description..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full md:w-80 px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-100 placeholder-slate-500 font-mono focus:outline-none focus:border-cyan-500"
        />

        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="detected">Detected</option>
            <option value="verified">Verified</option>
            <option value="remediated">Remediated</option>
            <option value="resolved">Resolved</option>
            <option value="false_positive">False Positive</option>
          </select>
        </div>
      </div>

      {/* Findings Table */}
      <div className="cyber-card rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px]">
              <tr>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Finding Title</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">CVSS</th>
                <th className="py-3 px-4">Verification Status</th>
                <th className="py-3 px-4">Responsible Owner</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {vulns.length > 0 ? (
                vulns.map((v) => (
                  <tr
                    key={v.id}
                    onClick={() => setSelectedVuln(v)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4">
                      <StatusBadge status={v.severity} size="xs" />
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-200 max-w-sm truncate">
                      {v.title}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300 text-[11px] uppercase">
                      {v.category.replace('_', ' ')}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-200">
                      {v.cvss_score.toFixed(1)}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={v.status} size="xs" />
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {v.responsible_owner}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button className="text-cyan-400 hover:text-cyan-300 font-mono text-xs flex items-center gap-1 ml-auto">
                        <span>Inspect</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No vulnerabilities found. Run a scan from the Security Scans page.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detailed Vulnerability Drawer */}
      {selectedVuln && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex justify-end animate-fadeIn">
          <div className="w-full max-w-2xl bg-[#0c1220] border-l border-slate-800 p-6 overflow-y-auto space-y-6">
            {/* Drawer Top */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <StatusBadge status={selectedVuln.severity} />
                <StatusBadge status={selectedVuln.status} />
                <span className="font-mono text-xs font-bold text-cyan-400">
                  CVSS {selectedVuln.cvss_score}
                </span>
              </div>
              <button
                onClick={() => setSelectedVuln(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Title & Description */}
            <div>
              <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">
                Vulnerability Reference #{selectedVuln.id}
              </p>
              <h3 className="text-lg font-bold text-white mt-1">
                {selectedVuln.title}
              </h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                {selectedVuln.description}
              </p>
            </div>

            {/* Business Impact Box */}
            {selectedVuln.business_impact && (
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs">
                <p className="font-bold text-rose-400 flex items-center gap-1.5 mb-1.5 font-mono uppercase text-[11px]">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Business & Financial Risk Evaluation</span>
                </p>
                <p className="text-slate-300 leading-relaxed">
                  {selectedVuln.business_impact}
                </p>
              </div>
            )}

            {/* Reproduction Evidence (Request / Response Dumps) */}
            {selectedVuln.evidence && selectedVuln.evidence.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono mb-2 flex items-center gap-1.5">
                  <Code className="w-4 h-4 text-cyan-400" />
                  <span>Minimal Proof Evidence (Agent 7 Verified)</span>
                </h4>

                <div className="space-y-3 font-mono text-[11px]">
                  <div>
                    <span className="text-slate-400 text-[10px] uppercase">HTTP Request Vector:</span>
                    <pre className="mt-1 p-3 rounded-lg bg-[#05070d] border border-slate-800 text-cyan-300 overflow-x-auto whitespace-pre-wrap">
                      {selectedVuln.evidence[0].request_dump || 'N/A'}
                    </pre>
                  </div>

                  <div>
                    <span className="text-slate-400 text-[10px] uppercase">Vulnerable HTTP Response:</span>
                    <pre className="mt-1 p-3 rounded-lg bg-[#05070d] border border-slate-800 text-rose-300 overflow-x-auto whitespace-pre-wrap">
                      {selectedVuln.evidence[0].response_dump || 'N/A'}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {/* Recommended Remediation */}
            {selectedVuln.remediation_guidance && (
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                <p className="font-bold text-emerald-400 flex items-center gap-1.5 mb-1.5 font-mono uppercase text-[11px]">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Recommended Developer Patch</span>
                </p>
                <p className="text-slate-300 leading-relaxed font-mono">
                  {selectedVuln.remediation_guidance}
                </p>
              </div>
            )}

            {/* Action Buttons: Verify (Agent 7), Remediate, Retest (Agent 10) */}
            <div className="pt-4 border-t border-slate-800 flex flex-wrap gap-3">
              <button
                onClick={() => handleVerify(selectedVuln.id)}
                disabled={actionInProgress}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 hover:bg-indigo-600/40 flex items-center gap-1.5 font-mono"
              >
                <FileCheck className="w-4 h-4" />
                <span>Verify Finding (Agent 7)</span>
              </button>

              <button
                onClick={() => setRemediationModal(true)}
                disabled={actionInProgress}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-600/40 flex items-center gap-1.5 font-mono"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Submit Developer Patch</span>
              </button>

              <button
                onClick={() => handleRetest(selectedVuln.id)}
                disabled={actionInProgress}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white flex items-center gap-1.5 font-mono shadow-lg shadow-cyan-600/20"
              >
                <RefreshCw className={`w-4 h-4 ${actionInProgress ? 'animate-spin' : ''}`} />
                <span>Retest Flaw (Agent 10)</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Remediation Modal */}
      {remediationModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0f172a] border border-slate-700 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span>Mark Remediation Applied</span>
            </h3>
            <p className="text-xs text-slate-300">
              Record the security fix or commit details. This will transition the finding into the "Remediated" state so Agent 10 can retest it.
            </p>
            <textarea
              rows={4}
              placeholder="Enter patch details or commit hash (e.g. Added session check, enforced tenant match)..."
              value={patchNotes}
              onChange={(e) => setPatchNotes(e.target.value)}
              className="w-full p-3 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setRemediationModal(false)}
                className="px-4 py-2 text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleRemediate}
                className="px-4 py-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-mono"
              >
                Confirm Patch
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

