import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { KpiCard, Card, Tabs } from '../components/shared';
import { ClaimsTable, AdjustersList } from '../components/ops';
import { useAuth } from '../auth/useAuth';
import { getOpsAnalytics, getAuditLogs, getOpsClaims } from '../api/clientApi';

const queueTabs = [
  { key: 'queue', label: 'Claims Queue' },
  { key: 'analytics', label: 'Analytics' },
  { key: 'audit', label: 'Audit Log' },
];

const OpsQueuePage = () => {
  const [activeTab, setActiveTab] = useState('queue');
  const [claims, setClaims] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { token } = useAuth();

  useEffect(() => {
    const loadData = async () => {
      if (!token) return;
      try {
        const [opsClaims, opsAnalytics, opsAuditLogs] = await Promise.all([
          getOpsClaims(token),
          getOpsAnalytics(token),
          getAuditLogs(token),
        ]);
        setClaims(opsClaims || []);
        setAnalytics(opsAnalytics || null);
        setAuditLogs(opsAuditLogs || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [token]);

  const handleSelectClaim = (claim) => {
    navigate(`/ops/case/${claim.claim_id || claim.id}`);
  };

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard title="Pending Settlements" value={loading ? '…' : analytics?.pending_human_review ?? 0} icon={Clock} />
        <KpiCard title="Avg Processing Time" value={loading ? '…' : analytics?.average_processing_time_seconds == null ? '—' : `${analytics.average_processing_time_seconds} sec`} icon={TrendingUp} />
        <KpiCard title="Override Rate" value={loading ? '…' : `${((analytics?.human_override_rate ?? 0) * 100).toFixed(1)}%`} icon={AlertTriangle} />
        <KpiCard title="Approval Rate" value={loading ? '…' : `${((analytics?.automated_approval_rate ?? 0) * 100).toFixed(1)}%`} icon={CheckCircle} />
      </div>

      {/* Main content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left — Tabbed content */}
        <div className="flex-1 min-w-0">
          <Card>
            <Tabs tabs={queueTabs} activeKey={activeTab} onChange={setActiveTab} className="px-5" />

            <div className="p-5">
              {activeTab === 'queue' && (
                <ClaimsTable claims={claims} loading={loading} onSelectClaim={handleSelectClaim} />
              )}

              {activeTab === 'analytics' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <Card className="p-5">
                      <h4 className="text-sm font-semibold text-primary mb-3">Claims Snapshot</h4>
                      <div className="space-y-3 text-sm text-secondary">
                        <div className="flex justify-between"><span>Total claims</span><span className="font-medium text-primary">{analytics?.total_claims_processed ?? 0}</span></div>
                        <div className="flex justify-between"><span>Approved</span><span className="font-medium text-primary">{analytics?.approved_claims ?? 0}</span></div>
                        <div className="flex justify-between"><span>Denied</span><span className="font-medium text-primary">{analytics?.denied_claims ?? 0}</span></div>
                        <div className="flex justify-between"><span>Pending</span><span className="font-medium text-primary">{analytics?.pending_human_review ?? 0}</span></div>
                      </div>
                    </Card>
                    <Card className="p-5">
                      <h4 className="text-sm font-semibold text-primary mb-3">Operations Health</h4>
                      <div className="space-y-3 text-sm text-secondary">
                        <div className="flex justify-between"><span>Human override rate</span><span className="font-medium text-primary">{((analytics?.human_override_rate ?? 0) * 100).toFixed(1)}%</span></div>
                        <div className="flex justify-between"><span>Automation rate</span><span className="font-medium text-primary">{((analytics?.automated_approval_rate ?? 0) * 100).toFixed(1)}%</span></div>
                        <div className="flex justify-between"><span>Audit entries</span><span className="font-medium text-primary">{auditLogs.length}</span></div>
                      </div>
                    </Card>
                  </div>
                </div>
              )}

              {activeTab === 'audit' && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-background">
                        <th className="text-left px-4 py-3 font-medium text-secondary">ID</th>
                        <th className="text-left px-4 py-3 font-medium text-secondary">Action</th>
                        <th className="text-left px-4 py-3 font-medium text-secondary">User</th>
                        <th className="text-left px-4 py-3 font-medium text-secondary">Target</th>
                        <th className="text-left px-4 py-3 font-medium text-secondary">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditLogs.map((log) => (
                        <tr key={log.id} className="border-t border-border">
                          <td className="px-4 py-3 font-medium text-accent">{log.id}</td>
                          <td className="px-4 py-3 text-primary">{log.action}</td>
                          <td className="px-4 py-3 text-primary">{log.agent_name || 'System'}</td>
                          <td className="px-4 py-3 text-secondary">{log.claim_id}</td>
                          <td className="px-4 py-3 text-secondary">{log.timestamp}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right — Adjusters */}
        <div className="lg:w-64 shrink-0">
          <Card className="p-5">
            <AdjustersList />
          </Card>
        </div>
      </div>
    </div>
  );
};

export default OpsQueuePage;
