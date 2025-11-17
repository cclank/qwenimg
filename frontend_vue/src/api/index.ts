import axios from 'axios'
import type { Task } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export const taskApi = {
  // 创建任务
  createTask(taskType: string, params: Record<string, any>, sessionId?: string) {
    return api.post<{ task_id: string; message: string }>('/tasks', {
      task_type: taskType,
      params,
      session_id: sessionId,
    })
  },

  // 获取任务状态
  getTask(taskId: string) {
    return api.get<Task>(`/tasks/${taskId}`)
  },

  // 获取任务历史
  getTasks(taskType?: string, status?: string) {
    return api.get<Task[]>('/tasks', {
      params: { task_type: taskType, status },
    })
  },

  // 删除任务
  deleteTask(taskId: string) {
    return api.delete(`/tasks/${taskId}`)
  },
}

export const healthApi = {
  check() {
    return api.get('/health')
  },
}
