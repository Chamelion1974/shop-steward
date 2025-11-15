/**
 * Modules page component (Hub Master only).
 */
import { useState } from 'react';
import Layout from '../components/Layout';
import ModuleConfigDialog from '../components/ModuleConfigDialog';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { Settings, Power, PowerOff, TrendingUp } from 'lucide-react';
import { ModuleStatus, Module } from '../types';

export default function ModulesPage() {
  const queryClient = useQueryClient();
  const [configModule, setConfigModule] = useState<Module | null>(null);

  const { data: modules, isLoading } = useQuery({
    queryKey: ['modules'],
    queryFn: () => api.getModules(),
  });

  const activateMutation = useMutation({
    mutationFn: (id: string) => api.activateModule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modules'] });
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => api.deactivateModule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modules'] });
    },
  });

  const updateConfigMutation = useMutation({
    mutationFn: ({ id, config }: { id: string; config: Record<string, any> }) =>
      api.updateModuleConfig(id, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modules'] });
    },
  });

  const handleToggleModule = (id: string, currentStatus: ModuleStatus) => {
    if (currentStatus === ModuleStatus.ACTIVE) {
      deactivateMutation.mutate(id);
    } else {
      activateMutation.mutate(id);
    }
  };

  const handleOpenConfig = (module: Module) => {
    setConfigModule(module);
  };

  const handleSaveConfig = (config: Record<string, any>) => {
    if (configModule) {
      updateConfigMutation.mutate({ id: configModule.id, config });
    }
  };

  const getStatusColor = (status: ModuleStatus) => {
    switch (status) {
      case ModuleStatus.ACTIVE:
        return 'badge-success';
      case ModuleStatus.ERROR:
        return 'badge-danger';
      default:
        return 'badge-info';
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Modules</h1>
          <p className="text-slate-600 mt-2">
            Manage and configure system modules
          </p>
        </div>

        {/* Modules Grid */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hub-primary mx-auto"></div>
          </div>
        ) : modules && modules.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((module) => (
              <div key={module.id} className="card">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-hub-primary rounded-lg">
                      <Settings className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        {module.display_name}
                      </h3>
                      <p className="text-xs text-slate-500">v{module.version}</p>
                    </div>
                  </div>
                  <span className={`badge ${getStatusColor(module.status)}`}>
                    {module.status}
                  </span>
                </div>

                {module.description && (
                  <p className="text-sm text-slate-600 mb-4">
                    {module.description}
                  </p>
                )}

                {module.last_run && (
                  <div className="flex items-center text-xs text-slate-500 mb-4">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    Last run: {new Date(module.last_run).toLocaleString()}
                  </div>
                )}

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleToggleModule(module.id, module.status)}
                    disabled={activateMutation.isPending || deactivateMutation.isPending}
                    className={`flex-1 btn ${
                      module.status === ModuleStatus.ACTIVE
                        ? 'btn-danger'
                        : 'btn-success'
                    }`}
                  >
                    {module.status === ModuleStatus.ACTIVE ? (
                      <>
                        <PowerOff className="w-4 h-4 mr-2" />
                        Deactivate
                      </>
                    ) : (
                      <>
                        <Power className="w-4 h-4 mr-2" />
                        Activate
                      </>
                    )}
                  </button>
                  <button 
                    className="btn-outline"
                    onClick={() => handleOpenConfig(module)}
                  >
                    Configure
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Settings className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 mb-4">No modules configured</p>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              Modules will appear here once they are registered in the system.
              Modules like Manufacturing Intelligence and Housekeeper can be
              activated and configured from this page.
            </p>
          </div>
        )}
      </div>

      {/* Configuration Dialog */}
      {configModule && (
        <ModuleConfigDialog
          module={configModule}
          isOpen={!!configModule}
          onClose={() => setConfigModule(null)}
          onSave={handleSaveConfig}
        />
      )}
    </Layout>
  );
}
