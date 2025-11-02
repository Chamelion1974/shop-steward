/**
 * Hub Master Dashboard page.
 */
import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { api } from '../services/api';
import {
  Briefcase,
  CheckSquare,
  Users,
  TrendingUp,
  AlertCircle,
  Activity,
} from 'lucide-react';
import { JobStatus, TaskStatus } from '../types';

export default function HubMasterDashboard() {
  const { data: jobsData } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => api.getJobs({ limit: 100 }),
  });

  const { data: tasksData } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => api.getTasks({ limit: 100 }),
  });

  const { data: users } = useQuery({
    queryKey: ['users'],
    queryFn: () => api.getUsers({ limit: 100 }),
  });

  const { data: modules } = useQuery({
    queryKey: ['modules'],
    queryFn: () => api.getModules(),
  });

  const jobs = jobsData?.jobs || [];
  const tasks = tasksData?.tasks || [];

  // Calculate statistics
  const stats = {
    totalJobs: jobs.length,
    activeJobs: jobs.filter(j => j.status === JobStatus.IN_PROGRESS).length,
    completedJobs: jobs.filter(j => j.status === JobStatus.COMPLETED).length,
    totalTasks: tasks.length,
    activeTasks: tasks.filter(t => t.status === TaskStatus.IN_PROGRESS).length,
    blockedTasks: tasks.filter(t => t.status === TaskStatus.BLOCKED).length,
    totalUsers: users?.length || 0,
    activeModules: modules?.filter(m => m.status === 'active').length || 0,
  };

  const statCards = [
    {
      name: 'Active Jobs',
      value: stats.activeJobs,
      total: stats.totalJobs,
      icon: Briefcase,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Tasks',
      value: stats.activeTasks,
      total: stats.totalTasks,
      icon: CheckSquare,
      color: 'bg-purple-500',
    },
    {
      name: 'Team Members',
      value: stats.totalUsers,
      total: null,
      icon: Users,
      color: 'bg-green-500',
    },
    {
      name: 'Blocked Tasks',
      value: stats.blockedTasks,
      total: null,
      icon: AlertCircle,
      color: 'bg-red-500',
    },
  ];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Hub Master Dashboard</h1>
          <p className="text-slate-600 mt-2">
            System overview and command center
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat) => (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-3 rounded-lg ${stat.color}`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-slate-600">{stat.name}</p>
                  <div className="flex items-baseline">
                    <p className="text-2xl font-semibold text-slate-900">{stat.value}</p>
                    {stat.total !== null && (
                      <p className="ml-2 text-sm text-slate-500">/ {stat.total}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent Activity & Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Jobs */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Recent Jobs</h2>
              <Activity className="w-5 h-5 text-slate-400" />
            </div>
            <div className="space-y-3">
              {jobs.slice(0, 5).map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900">{job.job_number}</p>
                    <p className="text-xs text-slate-600 truncate">{job.title}</p>
                  </div>
                  <span className={`badge ${
                    job.status === JobStatus.COMPLETED ? 'badge-success' :
                    job.status === JobStatus.IN_PROGRESS ? 'badge-primary' :
                    job.status === JobStatus.REVIEW ? 'badge-warning' :
                    'badge-info'
                  }`}>
                    {job.status.replace('_', ' ')}
                  </span>
                </div>
              ))}
              {jobs.length === 0 && (
                <p className="text-sm text-slate-500 text-center py-4">No jobs yet</p>
              )}
            </div>
          </div>

          {/* Module Status */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Module Status</h2>
              <TrendingUp className="w-5 h-5 text-slate-400" />
            </div>
            <div className="space-y-3">
              {modules && modules.length > 0 ? (
                modules.map((module) => (
                  <div
                    key={module.id}
                    className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900">{module.display_name}</p>
                      <p className="text-xs text-slate-600">Version {module.version}</p>
                    </div>
                    <span className={`badge ${
                      module.status === 'active' ? 'badge-success' :
                      module.status === 'error' ? 'badge-danger' :
                      'badge-info'
                    }`}>
                      {module.status}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <p className="text-sm text-slate-500 mb-4">No modules configured yet</p>
                  <a href="/modules" className="btn-primary text-sm">
                    Configure Modules
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
