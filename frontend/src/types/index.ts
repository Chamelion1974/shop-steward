/**
 * TypeScript types for The Hub frontend.
 */

export enum UserRole {
  HUB_MASTER = 'hub_master',
  HUB_CAP = 'hub_cap',
}

export enum JobPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum JobStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export enum TaskType {
  PROGRAMMING = 'programming',
  SETUP = 'setup',
  MACHINING = 'machining',
  INSPECTION = 'inspection',
  OTHER = 'other',
}

export enum TaskStatus {
  PENDING = 'pending',
  ASSIGNED = 'assigned',
  IN_PROGRESS = 'in_progress',
  BLOCKED = 'blocked',
  REVIEW = 'review',
  COMPLETED = 'completed',
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum ModuleStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ERROR = 'error',
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  skills: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  job_number: string;
  title: string;
  description?: string;
  customer?: string;
  priority: JobPriority;
  status: JobStatus;
  deadline?: string;
  files: any[];
  metadata: Record<string, any>;
  created_by: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface Task {
  id: string;
  job_id: string;
  title: string;
  description?: string;
  task_type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  assigned_to?: string;
  estimated_hours?: number;
  actual_hours?: number;
  dependencies: string[];
  blockers?: string;
  files: any[];
  comments: TaskComment[];
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface TaskComment {
  id: string;
  user_id: string;
  username: string;
  text: string;
  created_at: string;
}

export interface Module {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  version: string;
  status: ModuleStatus;
  config: Record<string, any>;
  metrics: Record<string, any>;
  last_run?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface CreateJobData {
  title: string;
  description?: string;
  customer?: string;
  priority: JobPriority;
  deadline?: string;
  assigned_to?: string;
  metadata?: Record<string, any>;
}

export interface UpdateJobData {
  title?: string;
  description?: string;
  customer?: string;
  priority?: JobPriority;
  status?: JobStatus;
  deadline?: string;
  assigned_to?: string;
  metadata?: Record<string, any>;
}

export interface CreateTaskData {
  job_id: string;
  title: string;
  description?: string;
  task_type: TaskType;
  priority: TaskPriority;
  estimated_hours?: number;
  assigned_to?: string;
  dependencies?: string[];
}

export interface UpdateTaskData {
  title?: string;
  description?: string;
  task_type?: TaskType;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigned_to?: string;
  estimated_hours?: number;
  actual_hours?: number;
  dependencies?: string[];
  blockers?: string;
}

export interface HousekeeperConfig {
  root_dir: string;
  hierarchical: boolean;
  enforce_naming: boolean;
  auto_rename: boolean;
  monitor_path?: string;
}

export interface WorkflowManagerConfig {
  workflow_dir: string;
}

export type ModuleConfig = HousekeeperConfig | WorkflowManagerConfig | Record<string, any>;
