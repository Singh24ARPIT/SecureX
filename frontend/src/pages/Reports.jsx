import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import {
  FileBarChart,
  Download,
  FileText,
  ShieldAlert,
  CheckCircle2,
  Printer
} from 'lucide-react';

export const Reports = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const res = await api.get('/reports/summary');
      setReport(res.data);
    } catch (err) {
      console.error('Failed to load report:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const downloadCsv = () => {
    window.open('/api/v1/reports/export/csv', '_blank');
  };

  const downloadJson = () => {
    window.open('/api/v1/reports/export/json', '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileBarChart className="w-5 h-5 text-cyan-400" />
            <span>Executive Security Reports & Analytics</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Agent 9 compiled executive report with business impact analysis and remediation roadmaps.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={downloadCsv}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 hover:text-white flex items-center gap-2 font-mono border border-slate-700"
          >
            <Download className="w-4 h-4 text-cyan-400" />
            <span>Download CSV</span>
          </button>
          <button
            onClick={downloadJson}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white flex items-center gap-2 font-mono shadow-lg shadow-cyan-600/20"
          >
            <Download className="w-4 h-4" />
            <span>Download JSON</span>
          </button>
        </div>
      </div>

      {/* Executive Summary Card */}
      <div className="cyber-card rounded-2xl p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-5">
          <div>
            <span className="text-[10px] font-mono font-bold uppercase text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
              VOYAGEHACK 4.0 AUDIT DOSSIER
            </span>
            <h3 className="text-lg font-bold text-white mt-1">
              {report?.title || 'Security Assessment Report'}
            </h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Platform: {report?.platform || 'SentinelAI DAST Engine'}
            </p>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-[10px] uppercase font-mono text-slate-500">Total Findings</p>
              <p className="text-2xl font-bold font-mono text-white">{report?.total_findings ?? 0}</p>
            </div>
            <div className="text-right">
              <p className="text-[10px] uppercase font-mono text-rose-400">Critical</p>
              <p className="text-2xl font-bold font-mono text-rose-400">
                {report?.severity_breakdown?.critical ?? 0}
              </p>
            </div>
          </div>
        </div>

        {/* Severity Summary Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-5 border-b border-slate-800 text-xs font-mono">
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
            <span className="text-rose-400 font-bold">CRITICAL: </span>
            <span className="text-white font-bold">{report?.severity_breakdown?.critical ?? 0}</span>
          </div>
          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <span className="text-amber-400 font-bold">HIGH: </span>
            <span className="text-white font-bold">{report?.severity_breakdown?.high ?? 0}</span>
          </div>
          <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
            <span className="text-purple-400 font-bold">MEDIUM: </span>
            <span className="text-white font-bold">{report?.severity_breakdown?.medium ?? 0}</span>
          </div>
          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <span className="text-blue-400 font-bold">LOW: </span>
            <span className="text-white font-bold">{report?.severity_breakdown?.low ?? 0}</span>
          </div>
        </div>

        {/* Findings Detail List */}
        <div className="pt-5 space-y-4">
          <h4 className="text-xs font-bold text-slate-200 uppercase font-mono tracking-wider">
            Detailed Finding Remediations & Technical Proof
          </h4>

          {report?.findings && report.findings.length > 0 ? (
            report.findings.map((item) => (
              <div key={item.id} className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <StatusBadge status={item.severity} size="xs" />
                    <span className="font-bold text-slate-100">{item.title}</span>
                  </div>
                  <span className="text-[11px] font-mono text-cyan-400">{item.affected_api}</span>
                </div>

                <p className="text-slate-300">{item.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-[11px]">
                  <div className="p-2.5 rounded bg-rose-500/5 border border-rose-500/15 text-slate-300">
                    <span className="text-rose-400 font-bold font-mono uppercase block mb-1">Business Impact</span>
                    {item.business_impact}
                  </div>
                  <div className="p-2.5 rounded bg-emerald-500/5 border border-emerald-500/15 text-slate-300">
                    <span className="text-emerald-400 font-bold font-mono uppercase block mb-1">Recommended Remediation</span>
                    {item.recommended_remediation}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500 py-4">No findings recorded in this report yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};
