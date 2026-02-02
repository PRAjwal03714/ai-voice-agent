// import React from 'react';
// import { useQuery } from '@tanstack/react-query';
// import { apiService } from '../services/api';
// import { StatsCard } from './StatsCard';
// import { IntentPieChart } from './IntentPieChart';
// import { CallsTable } from './CallsTable';
// import { Phone, TrendingUp, Clock, Target } from 'lucide-react';

// export const Dashboard: React.FC = () => {
//   const { data: calls, isLoading } = useQuery({
//     queryKey: ['recentCalls'],
//     queryFn: () => apiService.getRecentCalls(20),
//     refetchInterval: 5000,
//   });

//   const { data: activeCalls } = useQuery({
//     queryKey: ['activeCalls'],
//     queryFn: () => apiService.getActiveCalls(),
//     refetchInterval: 2000,
//   });

//   const stats = React.useMemo(() => {
//     if (!calls) return null;
    
//     const totalCalls = calls.length;
//     const qualified = calls.filter(c => c.intent === 'QUALIFIED').length;
//     const avgDuration = calls.reduce((sum, c) => sum + (c.call_duration || 0), 0) / totalCalls;
    
//     const intentDist: { [key: string]: number } = {};
//     calls.forEach(call => {
//       const intent = call.intent || "Unknown";
//       intentDist[intent] = (intentDist[intent] || 0) + 1;
//     });
    
//     return { totalCalls, qualified, avgDuration, intentDist };
//   }, [calls]);

//   if (isLoading || !stats) {
//     return (
//       <div className="flex items-center justify-center h-screen">
//         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-gray-100 p-6">
//       <div className="max-w-7xl mx-auto">
//         <h1 className="text-3xl font-bold text-gray-900 mb-8">Vanessa AI Dashboard</h1>
        
//         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
//           <StatsCard
//             title="Total Calls"
//             value={stats.totalCalls}
//             icon={<Phone className="w-6 h-6" />}
//           />
//           <StatsCard
//             title="Qualified Leads"
//             value={stats.qualified}
//             icon={<Target className="w-6 h-6" />}
//           />
//           <StatsCard
//             title="Avg Duration"
//             value={`${Math.floor(stats.avgDuration / 60)}:${Math.floor(stats.avgDuration % 60).toString().padStart(2, '0')}`}
//             icon={<Clock className="w-6 h-6" />}
//           />
//           <StatsCard
//             title="Active Calls"
//             value={activeCalls?.length || 0}
//             icon={<TrendingUp className="w-6 h-6" />}
//           />
//         </div>

//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
//           <div className="lg:col-span-1">
//             <IntentPieChart data={stats.intentDist} />
//           </div>
//           <div className="lg:col-span-2">
//             <CallsTable calls={calls || []} />
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };





import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiService, CallLog } from '../services/api';
import { StatsCard } from './StatsCard';
import { IntentPieChart } from './IntentPieChart';
import { CallsTable } from './CallsTable';
import { Phone, TrendingUp, Clock, Target } from 'lucide-react';

export const Dashboard: React.FC = () => {

  /* =========================
     Recent Calls
  ========================= */

  const {
    data: calls = [],
    isLoading,
    isError,
  } = useQuery<CallLog[]>({
    queryKey: ['recentCalls'],
    queryFn: async () => {
      const res = await apiService.getRecentCalls(20);
  
      // 🔥 CRITICAL FIX: normalize runtime data
      if (Array.isArray(res)) return res;
      if (Array.isArray((res as any)?.calls)) return (res as any).calls;
  
      return [];
    },
    refetchInterval: 5000,
  });
  

  /* =========================
     Active Calls
  ========================= */

  const { data: activeCalls = [] } = useQuery<string[]>({
    queryKey: ['activeCalls'],
    queryFn: async () => {
      const data = await apiService.getActiveCalls();
      return Array.isArray(data?.active_calls) ? data.active_calls : [];
    },
    refetchInterval: 2000,
  });

  /* =========================
     Derived Stats
  ========================= */

  const stats = React.useMemo(() => {
    const totalCalls = calls.length;

    const qualified = calls.filter(
      (call) => call.intent === 'QUALIFIED'
    ).length;

    const avgDuration =
      totalCalls > 0
        ? calls.reduce<number>(
            (sum, call) => sum + (call.call_duration ?? 0),
            0
          ) / totalCalls
        : 0;

    const intentDist: Record<string, number> = {};
    calls.forEach((call) => {
      const intent = call.intent ?? 'Unknown';
      intentDist[intent] = (intentDist[intent] || 0) + 1;
    });

    return {
      totalCalls,
      qualified,
      avgDuration,
      intentDist,
    };
  }, [calls]);

  /* =========================
     Loading / Error
  ========================= */

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center h-screen text-red-600">
        Failed to load dashboard data.
      </div>
    );
  }

  /* =========================
     Render
  ========================= */

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Vanessa AI Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Calls"
            value={stats.totalCalls}
            icon={<Phone className="w-6 h-6" />}
          />
          <StatsCard
            title="Qualified Leads"
            value={stats.qualified}
            icon={<Target className="w-6 h-6" />}
          />
          <StatsCard
            title="Avg Duration"
            value={`${Math.floor(stats.avgDuration / 60)}:${Math.floor(
              stats.avgDuration % 60
            )
              .toString()
              .padStart(2, '0')}`}
            icon={<Clock className="w-6 h-6" />}
          />
          <StatsCard
            title="Active Calls"
            value={activeCalls.length}
            icon={<TrendingUp className="w-6 h-6" />}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <IntentPieChart data={stats.intentDist} />
          </div>
          <div className="lg:col-span-2">
            <CallsTable calls={calls} />
          </div>
        </div>
      </div>
    </div>
  );
};
