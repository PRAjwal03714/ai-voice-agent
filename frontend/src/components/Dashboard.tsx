import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { StatsCard } from './StatsCard';
import { IntentPieChart } from './IntentPieChart';
import { CallsTable } from './CallsTable';
import { Phone, TrendingUp, Clock, Target } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { data: calls, isLoading } = useQuery({
    queryKey: ['recentCalls'],
    queryFn: () => apiService.getRecentCalls(20),
    refetchInterval: 5000,
  });

  const { data: activeCalls } = useQuery({
    queryKey: ['activeCalls'],
    queryFn: () => apiService.getActiveCalls(),
    refetchInterval: 2000,
  });

  const stats = React.useMemo(() => {
    if (!calls) return null;

    const totalCalls = calls.length;
    const qualified = calls.filter(c => c.intent === 'QUALIFIED').length;
    const avgDuration = calls.reduce((sum, c) => sum + c.call_duration, 0) / totalCalls;

    const intentDist: { [key: string]: number } = {};
    calls.forEach(call => {
      intentDist[call.intent] = (intentDist[call.intent] || 0) + 1;
    });

    return { totalCalls, qualified, avgDuration, intentDist };
  }, [calls]);

  if (isLoading || !stats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-900">🏡 Vanessa AI Dashboard</h1>
          <p className="text-sm text-gray-600 mt-1">Real-time analytics</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard title="Total Calls" value={stats.totalCalls} icon={<Phone size={32} />} />
          <StatsCard 
            title="Qualified Leads" 
            value={stats.qualified} 
            subtitle={`${((stats.qualified / stats.totalCalls) * 100).toFixed(1)}%`}
            icon={<Target size={32} />} 
          />
          <StatsCard 
            title="Avg Duration" 
            value={`${Math.floor(stats.avgDuration)}s`} 
            icon={<Clock size={32} />} 
          />
          <StatsCard 
            title="Active Calls" 
            value={activeCalls?.count || 0} 
            icon={<TrendingUp size={32} />} 
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <IntentPieChart data={stats.intentDist} />
        </div>

        <CallsTable calls={calls || []} />
      </main>
    </div>
  );
};
