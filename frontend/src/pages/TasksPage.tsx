/**
 * Tasks page component.
 */
import Layout from '../components/Layout';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { CheckSquare } from 'lucide-react';
import { TaskStatus, TaskPriority } from '../types';

export default function TasksPage() {
  const { data: tasksData, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => api.getTasks({ limit: 100 }),
  });

  const tasks = tasksData?.tasks || [];

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return 'badge-success';
      case TaskStatus.IN_PROGRESS:
        return 'badge-primary';
      case TaskStatus.REVIEW:
        return 'badge-warning';
      case TaskStatus.BLOCKED:
        return 'badge-danger';
      default:
        return 'badge-info';
    }
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT:
        return 'text-red-600';
      case TaskPriority.HIGH:
        return 'text-orange-600';
      case TaskPriority.MEDIUM:
        return 'text-blue-600';
      case TaskPriority.LOW:
        return 'text-slate-600';
      default:
        return 'text-slate-600';
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Tasks</h1>
          <p className="text-slate-600 mt-2">
            View and manage all tasks
          </p>
        </div>

        {/* Tasks List */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hub-primary mx-auto"></div>
          </div>
        ) : tasks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tasks.map((task) => (
              <div key={task.id} className="card">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-md font-semibold text-slate-900">
                    {task.title}
                  </h3>
                  <span className={`badge ${getStatusColor(task.status)}`}>
                    {task.status.replace('_', ' ')}
                  </span>
                </div>

                {task.description && (
                  <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                    {task.description}
                  </p>
                )}

                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Type:</span>
                    <span className="badge badge-info">{task.task_type}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Priority:</span>
                    <span className={getPriorityColor(task.priority)}>
                      {task.priority}
                    </span>
                  </div>
                  {task.estimated_hours && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Estimated:</span>
                      <span className="text-slate-700">{task.estimated_hours}h</span>
                    </div>
                  )}
                  {task.blockers && (
                    <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-700">
                      Blocked: {task.blockers}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <CheckSquare className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 mb-4">No tasks yet</p>
            <button className="btn-primary">Create Your First Task</button>
          </div>
        )}
      </div>
    </Layout>
  );
}
