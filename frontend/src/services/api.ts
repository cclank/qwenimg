/**
 * API服务
 */
import axios from 'axios';
import type {
  TextToImageRequest,
  ImageToVideoRequest,
  TextToVideoRequest,
  TaskResponse,
  Task,
  Inspiration,
} from '@/types';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * 生成任务相关API
 */
export const generationAPI = {
  // 文生图
  textToImage: (data: TextToImageRequest): Promise<TaskResponse> => {
    return api.post('/generation/text-to-image', data);
  },

  // 图生视频
  imageToVideo: (data: ImageToVideoRequest): Promise<TaskResponse> => {
    return api.post('/generation/image-to-video', data);
  },

  // 文生视频
  textToVideo: (data: TextToVideoRequest): Promise<TaskResponse> => {
    return api.post('/generation/text-to-video', data);
  },

  // 上传图片
  uploadImage: (formData: FormData): Promise<{ url: string }> => {
    return api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 获取任务状态
  getTaskStatus: (taskId: string): Promise<Task> => {
    return api.get(`/generation/task/${taskId}`);
  },

  // 获取任务列表
  getTasks: (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    task_type?: string;
    session_id?: string;
  }): Promise<{ tasks: Task[]; total: number; page: number; page_size: number }> => {
    return api.get('/generation/tasks', { params });
  },

  // 删除任务
  deleteTask: (taskId: string): Promise<{ message: string }> => {
    return api.delete(`/generation/task/${taskId}`);
  },
};

/**
 * 灵感相关API
 */
export const inspirationAPI = {
  // 获取灵感列表
  getList: (params?: {
    category?: string;
    task_type?: string;
    limit?: number;
  }): Promise<{ inspirations: Inspiration[]; total: number; categories: string[] }> => {
    return api.get('/inspiration/list', { params });
  },

  // 获取灵感详情
  getDetail: (id: number): Promise<Inspiration> => {
    return api.get(`/inspiration/${id}`);
  },

  // 点赞
  like: (id: number): Promise<{ message: string; likes: number }> => {
    return api.post(`/inspiration/${id}/like`);
  },

  // 获取分类列表
  getCategories: (): Promise<{ categories: string[] }> => {
    return api.get('/inspiration/categories/list');
  },
};

export default api;
