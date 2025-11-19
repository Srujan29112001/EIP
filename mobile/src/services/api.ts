/**
 * API Service
 * Handles all API communication with EIP backend
 */
import axios, {AxiosInstance, AxiosRequestConfig, AxiosResponse} from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      async (config: AxiosRequestConfig) => {
        const token = await AsyncStorage.getItem('access_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      error => {
        return Promise.reject(error);
      },
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      async error => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh or logout
          await this.handleUnauthorized();
        }
        return Promise.reject(error);
      },
    );
  }

  private async handleUnauthorized() {
    // Clear stored token
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('user_info');
    // Navigate to login screen (handled by navigation)
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {email, password});
    const {access_token} = response.data;
    await AsyncStorage.setItem('access_token', access_token);
    return response.data;
  }

  async register(email: string, name: string, password: string, tier: string) {
    const response = await this.client.post('/auth/register', {
      email,
      name,
      password,
      tier,
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    await AsyncStorage.setItem('user_info', JSON.stringify(response.data));
    return response.data;
  }

  // Chat endpoints
  async sendChatMessage(query: string, sessionId: string) {
    const response = await this.client.post('/chat', {
      query,
      session_id: sessionId,
    });
    return response.data;
  }

  async getChatHistory(sessionId: string) {
    const response = await this.client.get(`/chat/history/${sessionId}`);
    return response.data;
  }

  // Document analysis endpoints
  async uploadDocument(file: FormData) {
    const response = await this.client.post('/analyze/document', file, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async analyzeImage(file: FormData, prompt: string) {
    const response = await this.client.post('/analyze/image', file, {
      params: {prompt},
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardMetrics() {
    const response = await this.client.get('/dashboard/metrics');
    return response.data;
  }

  async getRecentInsights() {
    const response = await this.client.get('/dashboard/insights');
    return response.data;
  }
}

export const api = new APIService();
export default api;
