/**
 * Module configuration dialog component.
 */
import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import type { Module } from '../types';

interface ModuleConfigDialogProps {
  module: Module;
  isOpen: boolean;
  onClose: () => void;
  onSave: (config: Record<string, any>) => void;
}

export default function ModuleConfigDialog({
  module,
  isOpen,
  onClose,
  onSave,
}: ModuleConfigDialogProps) {
  const [config, setConfig] = useState<Record<string, any>>(module.config || {});

  useEffect(() => {
    setConfig(module.config || {});
  }, [module]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(config);
    onClose();
  };

  const handleChange = (key: string, value: any) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const renderConfigFields = () => {
    switch (module.name) {
      case 'housekeeper':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Root Directory
              </label>
              <input
                type="text"
                value={config.root_dir || ''}
                onChange={(e) => handleChange('root_dir', e.target.value)}
                placeholder="C:/Users/YourName/ShopSteward/files"
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">
                Default: {'{home}'}/ShopSteward/files - Directory where files will be organized
              </p>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.hierarchical || false}
                  onChange={(e) => handleChange('hierarchical', e.target.checked)}
                  className="rounded border-slate-300 text-hub-primary focus:ring-hub-primary mr-2"
                />
                <span className="text-sm font-medium text-slate-700">
                  Hierarchical Structure
                </span>
              </label>
              <p className="text-xs text-slate-500 mt-1 ml-6">
                Organize files by customer in a hierarchical structure
              </p>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.enforce_naming || false}
                  onChange={(e) => handleChange('enforce_naming', e.target.checked)}
                  className="rounded border-slate-300 text-hub-primary focus:ring-hub-primary mr-2"
                />
                <span className="text-sm font-medium text-slate-700">
                  Enforce Naming Conventions
                </span>
              </label>
              <p className="text-xs text-slate-500 mt-1 ml-6">
                Require files to follow naming conventions
              </p>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.auto_rename || false}
                  onChange={(e) => handleChange('auto_rename', e.target.checked)}
                  className="rounded border-slate-300 text-hub-primary focus:ring-hub-primary mr-2"
                />
                <span className="text-sm font-medium text-slate-700">
                  Auto Rename Files
                </span>
              </label>
              <p className="text-xs text-slate-500 mt-1 ml-6">
                Automatically rename files to match conventions
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Monitor Path (Optional)
              </label>
              <input
                type="text"
                value={config.monitor_path || ''}
                onChange={(e) => handleChange('monitor_path', e.target.value)}
                placeholder="C:/Users/YourName/Downloads"
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">
                Directory to monitor for new files (leave empty to disable)
              </p>
            </div>
          </>
        );

      case 'workflow_manager':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Workflow Directory
              </label>
              <input
                type="text"
                value={config.workflow_dir || ''}
                onChange={(e) => handleChange('workflow_dir', e.target.value)}
                placeholder="C:/Users/YourName/ShopSteward/workflow"
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">
                Default: {'{home}'}/ShopSteward/workflow - Directory where workflow data will be stored
              </p>
            </div>
          </>
        );

      default:
        return (
          <div className="text-center py-8">
            <p className="text-slate-500">
              This module has no configurable options.
            </p>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              Configure {module.display_name}
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Customize module settings
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
            title="Close"
            aria-label="Close dialog"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-6">
            {renderConfigFields()}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-3 p-6 border-t border-slate-200 bg-slate-50">
            <button
              type="button"
              onClick={onClose}
              className="btn-outline"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
            >
              Save Configuration
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
