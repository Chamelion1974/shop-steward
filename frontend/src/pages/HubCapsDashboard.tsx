/**
 * Hub Caps Dashboard page.
 */
import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { api } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import {
  CheckSquare,
  Clock,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
import { TaskStatus, TaskPriority } from '../types';

export default function HubCapsDashboard() {
  const { user } = useAuthStore();

  const { data: tasksData } = useQuery({
    queryKey: ['my-tasks', user?.id],
    queryFn: () => api.getTasks({ assigned_to: user?.id, limit: 100 }),
  });

  const tasks = tasksData?.tasks || [];

  // Calculate statistics
  const stats = {
    totalTasks: tasks.length,
    inProgress: tasks.filter(t => t.status === TaskStatus.IN_PROGRESS).length,
    pending: tasks.filter(t => t.status === TaskStatus.PENDING || t.status === TaskStatus.ASSIGNED).length,
    blocked: tasks.filter(t => t.status === TaskStatus.BLOCKED).length,
    completed: tasks.filter(t => t.status === TaskStatus.COMPLETED).length,
  };

  const statCards = [
    {
      name: 'In Progress',
      value: stats.inProgress,
      icon: Clock,
      color: 'bg-blue-500',
    },
    {
      name: 'Pending',
      value: stats.pending,
      icon: CheckSquare,
      color: 'bg-purple-500',
    },
    {
      name: 'Blocked',
      value: stats.blocked,
      icon: AlertCircle,
      color: 'bg-red-500',
    },
    {
      name: 'Completed',
      value: stats.completed,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
  ];

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT:
        return 'badge-danger';
      case TaskPriority.HIGH:
        return 'badge-warning';
      case TaskPriority.MEDIUM:
        return 'badge-primary';
      case TaskPriority.LOW:
        return 'badge-info';
      default:
        return 'badge-info';
    }
  };

  const activeTasks = tasks.filter(
    t => t.status === TaskStatus.IN_PROGRESS || t.status === TaskStatus.ASSIGNED
  );

  const pendingTasks = tasks.filter(t => t.status === TaskStatus.PENDING);

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Welcome back, {user?.full_name}!
          </h1>
          <p className="text-slate-600 mt-2">
            Here's what's on your plate today
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
                  <p className="text-2xl font-semibold text-slate-900">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Tasks Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Active Tasks */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Active Tasks</h2>
              <span className="badge-primary">{activeTasks.length}</span>
            </div>
            <div className="space-y-3">
              {activeTasks.length > 0 ? (
                activeTasks.map((task) => (
                  <div
                    key={task.id}
                    className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-sm font-medium text-slate-900">{task.title}</h3>
                      <span className={`badge ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                    </div>
                    {task.description && (
                      <p className="text-xs text-slate-600 mb-2 line-clamp-2">
                        {task.description}
                      </p>
                    )}
                    <div className="flex items-center text-xs text-slate-500">
                      <span className="badge badge-info mr-2">{task.task_type}</span>
                      {task.estimated_hours && (
                        <span>Est: {task.estimated_hours}h</span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm text-slate-500">No active tasks</p>
                </div>
              )}
            </div>
          </div>

          {/* Pending Tasks */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Pending Tasks</h2>
              <span className="badge-warning">{pendingTasks.length}</span>
            </div>
            <div className="space-y-3">
              {pendingTasks.length > 0 ? (
                pendingTasks.map((task) => (
                  <div
                    key={task.id}
                    className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-sm font-medium text-slate-900">{task.title}</h3>
                      <span className={`badge ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                    </div>
                    {task.description && (
                      <p className="text-xs text-slate-600 mb-2 line-clamp-2">
                        {task.description}
                      </p>
                    )}
                    <div className="flex items-center text-xs text-slate-500">
                      <span className="badge badge-info mr-2">{task.task_type}</span>
                      {task.estimated_hours && (
                        <span>Est: {task.estimated_hours}h</span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <CheckSquare className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm text-slate-500">No pending tasks</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
