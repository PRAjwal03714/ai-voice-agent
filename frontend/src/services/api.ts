// API Base URL - uses environment variable or defaults to production
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://vanessa-ai-backend.onrender.com';

// Types
export interface CallLog {
  id?: string;  // Added id field
  call_sid: string;
  phone_number?: string;
  phone?: string;  // Alternative field name
  intent?: string;
  price_mentioned?: number;
  timeline_mentioned?: string;
  call_duration?: number;
  created_at: string;
}

export interface Stats {
  total_calls: number;
  qualified_leads: number;
  avg_call_duration: number;
  intent_distribution: { [key: string]: number };
}

// API Service
export const apiService = {
  // Get active calls
  getActiveCalls: async () => {
    const response = await fetch(`${API_BASE_URL}/active-calls`);
    if (!response.ok) throw new Error('Failed to fetch active calls');
    return response.json();
  },

  // Get recent calls
  getRecentCalls: async (): Promise<CallLog[]> => {
    const response = await fetch(`${API_BASE_URL}/recent-calls`);
    if (!response.ok) throw new Error('Failed to fetch recent calls');
    return response.json();
  },

  // Get dashboard stats
  getStats: async (): Promise<Stats> => {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },

  // Get transcripts
  getTranscripts: async () => {
    const response = await fetch(`${API_BASE_URL}/api/transcripts`);
    if (!response.ok) throw new Error('Failed to fetch transcripts');
    return response.json();
  },

  // Export calls as CSV
  exportCallsCSV: async () => {
    const response = await fetch(`${API_BASE_URL}/api/export/csv`);
    if (!response.ok) throw new Error('Failed to export CSV');
    return response.blob();
  }
};

export default API_BASE_URL;