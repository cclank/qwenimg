/**
 * 全局状态管理 - Zustand
 */
import { create } from 'zustand';
import type { Task, TaskType } from '@/types';

// 生成简单的UUID
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

// 安全获取localStorage
const getStoredApiKey = () => {
  if (typeof window !== 'undefined' && window.localStorage) {
    return localStorage.getItem('dashscope_api_key') || '';
  }
  return '';
};

// 安全获取或生成session_id
const getOrGenerateSessionId = () => {
  if (typeof window !== 'undefined' && window.localStorage) {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = generateUUID();
      localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  }
  return generateUUID();
};

interface AppState {
  // 会话ID
  sessionId: string;

  // 任务列表
  tasks: Task[];

  // 当前活跃的Tab
  activeTab: TaskType | 'history' | 'inspiration';

  // API Key配置
  apiKey: string;

  // 图生视频预填充图片URL
  imageToVideoUrl: string;

  // 操作方法
  setSessionId: (sessionId: string) => void;
  addTask: (task: Task) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  removeTask: (taskId: string) => void;
  removeTaskResult: (taskId: string, url: string) => void;
  setActiveTab: (tab: TaskType | 'history' | 'inspiration') => void;
  setApiKey: (apiKey: string) => void;
  clearTasks: () => void;
  setImageToVideoUrl: (url: string) => void;

  // 删除确认设置
  skipDeleteConfirm: boolean;
  setSkipDeleteConfirm: (skip: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // 初始状态
  sessionId: getOrGenerateSessionId(),
  tasks: [],
  activeTab: 'text_to_image',
  apiKey: getStoredApiKey(),
  imageToVideoUrl: '',
  skipDeleteConfirm: typeof window !== 'undefined' && window.localStorage ? localStorage.getItem('skip_delete_confirm') === 'true' : false,

  // 设置会话ID
  setSessionId: (sessionId) => set({ sessionId }),

  // 添加任务（避免重复）
  addTask: (task) =>
    set((state) => {
      // 检查任务是否已存在
      const taskExists = state.tasks.some(t => t.task_id === task.task_id);
      if (taskExists) {
        // 如果任务已存在，更新而不是添加
        return {
          tasks: state.tasks.map((t) =>
            t.task_id === task.task_id ? { ...t, ...task } : t
          ),
        };
      } else {
        // 如果任务不存在，添加到开头
        return {
          tasks: [task, ...state.tasks],
        };
      }
    }),

  // 更新任务
  updateTask: (taskId, updates) =>
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.task_id === taskId ? { ...task, ...updates } : task
      ),
    })),

  // 删除任务
  removeTask: (taskId) =>
    set((state) => ({
      tasks: state.tasks.filter((task) => task.task_id !== taskId),
    })),

  // 删除任务中的特定结果
  removeTaskResult: (taskId, url) =>
    set((state) => {
      const task = state.tasks.find((t) => t.task_id === taskId);
      if (!task || !task.result_urls) return {};

      const newResultUrls = task.result_urls.filter((u) => u !== url);

      // 如果没有剩余结果，删除整个任务
      if (newResultUrls.length === 0) {
        return {
          tasks: state.tasks.filter((t) => t.task_id !== taskId),
        };
      }

      // 否则更新任务的result_urls
      return {
        tasks: state.tasks.map((t) =>
          t.task_id === taskId ? { ...t, result_urls: newResultUrls } : t
        ),
      };
    }),

  // 切换Tab
  setActiveTab: (tab) => set({ activeTab: tab }),

  // 设置API Key
  setApiKey: (apiKey) => {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('dashscope_api_key', apiKey);
    }
    set({ apiKey });
  },

  // 清空任务
  clearTasks: () => set({ tasks: [] }),

  // 设置图生视频URL
  // 设置图生视频URL
  setImageToVideoUrl: (url) => set({ imageToVideoUrl: url }),

  // 设置是否跳过删除确认
  setSkipDeleteConfirm: (skip) => {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('skip_delete_confirm', String(skip));
    }
    set({ skipDeleteConfirm: skip });
  },
}));
