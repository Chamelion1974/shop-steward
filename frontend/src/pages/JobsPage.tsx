/**
 * Jobs page component.
 */
import Layout from '../components/Layout';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Briefcase } from 'lucide-react';
import { JobStatus, JobPriority } from '../types';

export default function JobsPage() {
  const { data: jobsData, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => api.getJobs({ limit: 100 }),
  });

  const jobs = jobsData?.jobs || [];

  const getStatusColor = (status: JobStatus) => {
    switch (status) {
      case JobStatus.COMPLETED:
        return 'badge-success';
      case JobStatus.IN_PROGRESS:
        return 'badge-primary';
      case JobStatus.REVIEW:
        return 'badge-warning';
      case JobStatus.CANCELLED:
        return 'badge-danger';
      default:
        return 'badge-info';
    }
  };

  const getPriorityColor = (priority: JobPriority) => {
    switch (priority) {
      case JobPriority.URGENT:
        return 'text-red-600';
      case JobPriority.HIGH:
        return 'text-orange-600';
      case JobPriority.MEDIUM:
        return 'text-blue-600';
      case JobPriority.LOW:
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
          <h1 className="text-3xl font-bold text-slate-900">Jobs</h1>
          <p className="text-slate-600 mt-2">
            Manage and track all production jobs
          </p>
        </div>

        {/* Jobs List */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hub-primary mx-auto"></div>
          </div>
        ) : jobs.length > 0 ? (
          <div className="grid grid-cols-1 gap-4">
            {jobs.map((job) => (
              <div key={job.id} className="card">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Briefcase className="w-5 h-5 text-hub-primary" />
                      <h3 className="text-lg font-semibold text-slate-900">
                        {job.job_number}
                      </h3>
                      <span className={`badge ${getStatusColor(job.status)}`}>
                        {job.status.replace('_', ' ')}
                      </span>
                    </div>
                    <h4 className="text-md font-medium text-slate-700 mb-2">
                      {job.title}
                    </h4>
                    {job.description && (
                      <p className="text-sm text-slate-600 mb-3">{job.description}</p>
                    )}
                    <div className="flex items-center space-x-4 text-sm text-slate-500">
                      {job.customer && (
                        <span>Customer: {job.customer}</span>
                      )}
                      <span className={getPriorityColor(job.priority)}>
                        Priority: {job.priority}
                      </span>
                      {job.deadline && (
                        <span>Deadline: {new Date(job.deadline).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 mb-4">No jobs yet</p>
            <button className="btn-primary">Create Your First Job</button>
          </div>
        )}
      </div>
    </Layout>
  );
}
