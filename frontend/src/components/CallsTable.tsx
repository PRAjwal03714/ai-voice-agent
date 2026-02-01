import React from 'react';
import { CallLog } from '../services/api';

interface CallsTableProps {
  calls: CallLog[];
}

export const CallsTable: React.FC<CallsTableProps> = ({ calls }) => {
  const getIntentBadge = (intent: string) => {
    const colors: { [key: string]: string } = {
      QUALIFIED: 'bg-blue-100 text-blue-800',
      INTERESTED: 'bg-green-100 text-green-800',
      NOT_INTERESTED: 'bg-red-100 text-red-800',
      EXPLORING: 'bg-yellow-100 text-yellow-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[intent] || 'bg-gray-100 text-gray-800'}`}>
        {intent}
      </span>
    );
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recent Calls</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Intent</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timeline</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {calls.map((call) => (
              <tr key={call.call_sid || call.id} className="hover:bg-gray-50">
<td className="px-6 py-4 text-sm font-medium text-gray-900">
  {call.phone_number || call.phone || 'Unknown'}
</td>                <td className="px-6 py-4">{getIntentBadge(call.intent)}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{call.price_mentioned || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{call.timeline_mentioned || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{formatDuration(call.call_duration)}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{formatDate(call.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
