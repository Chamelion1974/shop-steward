/**
 * API service for The Hub.
 */
import axios, { AxiosInstance } from 'axios';
import type {
  AuthTokens,
  LoginCredentials,
  User,
  Job,
  Task,
  Module,
  CreateJobData,
  UpdateJobData,
  CreateTaskData,
  UpdateTaskData,
} from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // If 401 and not already retried, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await axios.post('/api/auth/refresh', {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token } = response.data;
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', refresh_token);

              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            } catch (refreshError) {
              // Refresh failed, logout user
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
              return Promise.reject(refreshError);
            }
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await this.client.post<AuthTokens>('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // Job endpoints
  async getJobs(params?: {
    status?: string;
    assigned_to?: string;
    customer?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ total: number; jobs: Job[] }> {
    const response = await this.client.get('/jobs', { params });
    return response.data;
  }

  async getJob(id: string): Promise<Job> {
    const response = await this.client.get<Job>(`/jobs/${id}`);
    return response.data;
  }

  async createJob(data: CreateJobData): Promise<Job> {
    const response = await this.client.post<Job>('/jobs', data);
    return response.data;
  }

  async updateJob(id: string, data: UpdateJobData): Promise<Job> {
    const response = await this.client.patch<Job>(`/jobs/${id}`, data);
    return response.data;
  }

  async deleteJob(id: string): Promise<void> {
    await this.client.delete(`/jobs/${id}`);
  }

  // Task endpoints
  async getTasks(params?: {
    job_id?: string;
    status?: string;
    assigned_to?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ total: number; tasks: Task[] }> {
    const response = await this.client.get('/tasks', { params });
    return response.data;
  }

  async getTask(id: string): Promise<Task> {
    const response = await this.client.get<Task>(`/tasks/${id}`);
    return response.data;
  }

  async createTask(data: CreateTaskData): Promise<Task> {
    const response = await this.client.post<Task>('/tasks', data);
    return response.data;
  }

  async updateTask(id: string, data: UpdateTaskData): Promise<Task> {
    const response = await this.client.patch<Task>(`/tasks/${id}`, data);
    return response.data;
  }

  async deleteTask(id: string): Promise<void> {
    await this.client.delete(`/tasks/${id}`);
  }

  async addTaskComment(id: string, text: string): Promise<Task> {
    const response = await this.client.post<Task>(`/tasks/${id}/comments`, { text });
    return response.data;
  }

  // User endpoints
  async getUsers(params?: { skip?: number; limit?: number }): Promise<User[]> {
    const response = await this.client.get<User[]>('/users', { params });
    return response.data;
  }

  async getUser(id: string): Promise<User> {
    const response = await this.client.get<User>(`/users/${id}`);
    return response.data;
  }

  // Module endpoints
  async getModules(): Promise<Module[]> {
    const response = await this.client.get<Module[]>('/modules');
    return response.data;
  }

  async getModule(id: string): Promise<Module> {
    const response = await this.client.get<Module>(`/modules/${id}`);
    return response.data;
  }

  async activateModule(id: string): Promise<Module> {
    const response = await this.client.post<Module>(`/modules/${id}/activate`);
    return response.data;
  }

  async deactivateModule(id: string): Promise<Module> {
    const response = await this.client.post<Module>(`/modules/${id}/deactivate`);
    return response.data;
  }

  async updateModuleConfig(id: string, config: Record<string, any>): Promise<Module> {
    const response = await this.client.patch<Module>(`/modules/${id}/config`, { config });
    return response.data;
  }

  async getModuleMetrics(id: string): Promise<any> {
    const response = await this.client.get(`/modules/${id}/metrics`);
    return response.data;
  }
}

export const api = new ApiService();
