/**
 * 全局状态管理 - Zustand
 */
import { create } from 'zustand';
import type { Task, TaskType } from '@/types';
import { v4 as uuidv4 } from 'uuid';

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
  sessionId: uuidv4(),
  tasks: [],
  activeTab: 'text_to_image',
  apiKey: localStorage.getItem('dashscope_api_key') || '',

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
    localStorage.setItem('dashscope_api_key', apiKey);
    set({ apiKey });
  },

  // 清空任务
  clearTasks: () => set({ tasks: [] }),
}));
