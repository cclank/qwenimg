/**
 * 全局状态管理 - Zustand
 */
import { create } from 'zustand';
import type { Task, TaskType } from '@/types';

// 生成简单的UUID
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
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

interface AppState {
  // 会话ID
  sessionId: string;

  // 任务列表
  tasks: Task[];

  // 当前活跃的Tab
  activeTab: TaskType | 'history' | 'inspiration';

  // API Key配置
  apiKey: string;

  // 操作方法
  setSessionId: (sessionId: string) => void;
  addTask: (task: Task) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  removeTask: (taskId: string) => void;
  setActiveTab: (tab: TaskType | 'history' | 'inspiration') => void;
  setApiKey: (apiKey: string) => void;
  clearTasks: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // 初始状态
  sessionId: generateUUID(),
  tasks: [],
  activeTab: 'text_to_image',
  apiKey: getStoredApiKey(),

  // 设置会话ID
  setSessionId: (sessionId) => set({ sessionId }),

  // 添加任务
  addTask: (task) =>
    set((state) => ({
      tasks: [task, ...state.tasks],
    })),

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
}));
