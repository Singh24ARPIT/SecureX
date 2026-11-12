import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { ApiDiscovery } from './pages/ApiDiscovery';
import { ApiInventory } from './pages/ApiInventory';
import { SecurityScanning } from './pages/SecurityScanning';
import { Vulnerabilities } from './pages/Vulnerabilities';
import { AgentActivity } from './pages/AgentActivity';
import { Reports } from './pages/Reports';
import { StagingTestbed } from './pages/StagingTestbed';
import { TargetManagement } from './pages/TargetManagement';
import { AuditLogs } from './pages/AuditLogs';
import { Login } from './pages/Login';

const ProtectedLayout = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#070a12] flex items-center justify-center text-cyan-400 font-mono text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
          <span>AUTHENTICATING SECUREX ENCLAVE...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-[#070a12]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/discovery" element={<ApiDiscovery />} />
              <Route path="/inventory" element={<ApiInventory />} />
              <Route path="/scans" element={<SecurityScanning />} />
              <Route path="/vulnerabilities" element={<Vulnerabilities />} />
              <Route path="/agents" element={<AgentActivity />} />
              <Route path="/staging-testbed" element={<StagingTestbed />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/targets" element={<TargetManagement />} />
              <Route path="/audit" element={<AuditLogs />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

