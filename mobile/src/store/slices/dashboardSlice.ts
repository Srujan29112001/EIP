/**
 * Dashboard Slice
 * Manages dashboard data and metrics
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

interface DashboardMetrics {
  revenue: number;
  revenue_growth: number;
  cash_balance: number;
  runway_months: number;
  customer_count: number;
  mrr: number;
  burn_rate: number;
}

interface DashboardState {
  metrics: DashboardMetrics | null;
  alerts: Array<{
    id: string;
    type: 'info' | 'warning' | 'critical';
    title: string;
    message: string;
    timestamp: string;
  }>;
  news: Array<{
    id: string;
    title: string;
    summary: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    source: string;
    published_at: string;
  }>;
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  metrics: null,
  alerts: [],
  news: [],
  loading: false,
  error: null,
};

// Async thunks
export const fetchDashboardData = createAsyncThunk(
  'dashboard/fetchData',
  async (userId: string, { rejectWithValue }) => {
    try {
      const data = await api.getDashboardData(userId);
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchAlerts = createAsyncThunk(
  'dashboard/fetchAlerts',
  async (userId: string, { rejectWithValue }) => {
    try {
      const alerts = await api.getAlerts(userId);
      return alerts;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    clearDashboard: (state) => {
      state.metrics = null;
      state.alerts = [];
      state.news = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardData.fulfilled, (state, action) => {
        state.loading = false;
        state.metrics = action.payload.metrics;
        state.news = action.payload.news;
      })
      .addCase(fetchDashboardData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    builder
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.alerts = action.payload;
      });
  },
});

export const { clearDashboard } = dashboardSlice.actions;
export default dashboardSlice.reducer;
