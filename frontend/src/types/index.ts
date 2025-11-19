/**
 * 类型定义
 */

export type TaskType = 'text_to_image' | 'image_to_video' | 'text_to_video';

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface Task {
  task_id: string;
  task_type: TaskType;
  status: TaskStatus;
  progress: number;
  prompt?: string;
  result_urls?: string[];
  error_message?: string;
  created_at?: string;
  completed_at?: string;
  image_count?: number;
}

export interface TextToImageRequest {
  prompt: string;
  negative_prompt?: string;
  model?: string;
  n?: number;
  size?: string;
  seed?: number;
  watermark?: boolean;
  session_id?: string;
}

export interface ImageToVideoRequest {
  image_url: string;
  prompt?: string;
  negative_prompt?: string;
  model?: string;
  resolution?: string;
  duration?: number;
  audio_url?: string;
  seed?: number;
  watermark?: boolean;
  session_id?: string;
}

export interface TextToVideoRequest {
  prompt: string;
  negative_prompt?: string;
  model?: string;
  resolution?: string;
  duration?: number;
  seed?: number;
  watermark?: boolean;
  session_id?: string;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface Inspiration {
  id: number;
  category: string;
  title: string;
  prompt: string;
  negative_prompt?: string;
  thumbnail_url?: string;
  task_type: TaskType;
  tags?: string[];
  likes: number;
  created_at: string;
}

export interface WSMessage {
  type: 'connected' | 'progress' | 'task_completed' | 'task_failed' | 'pong';
  task_id?: string;
  session_id?: string;
  message?: string;
  data?: any;
}
