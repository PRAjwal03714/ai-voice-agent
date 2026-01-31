import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface CallLog {
  id: number;
  phone_number: string;
  phone?: string;  // ← Add this as optional
  intent: string;
  price_mentioned: string | null;
  price?: string | null;  // ← Add this as optional
  timeline_mentioned: string | null;
  timeline?: string | null;  // ← Add this as optional
  call_duration: number;
  duration?: number;  // ← Add this as optional
  created_at: string;
}

export interface DashboardStats {
  total_calls: number;
  qualified_leads: number;
  avg_duration: number;
  intent_distribution: {
    [key: string]: number;
  };
}

export const apiService = {
  getRecentCalls: async (limit: number = 10): Promise<CallLog[]> => {
    const response = await api.get(`/recent-calls`);
    return response.data.calls;
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/stats');
    return response.data;
  },

  getActiveCalls: async () => {
    const response = await api.get('/active-calls');
    return response.data;
  },

  getTranscripts: async (limit: number = 10) => {
    const response = await api.get(`/api/transcripts?limit=${limit}`);
    return response.data.transcripts;
  },
};

export default api;
