import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Task } from '../types'

export const useAppStore = defineStore('app', () => {
  // 状态
  const sessionId = ref(`session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)
  const tasks = ref<Map<string, Task>>(new Map())
  const ws = ref<WebSocket | null>(null)

  // 计算属性
  const activeTasks = computed(() => {
    return Array.from(tasks.value.values()).filter(
      (task) => task.status === 'pending' || task.status === 'processing'
    )
  })

  const completedTasks = computed(() => {
    return Array.from(tasks.value.values()).filter(
      (task) => task.status === 'completed'
    )
  })

  // 方法
  function addTask(task: Task) {
    tasks.value.set(task.task_id, task)
  }

  function updateTask(taskId: string, updates: Partial<Task>) {
    const task = tasks.value.get(taskId)
    if (task) {
      tasks.value.set(taskId, { ...task, ...updates })
    }
  }

  function removeTask(taskId: string) {
    tasks.value.delete(taskId)
  }

  function connectWebSocket() {
    if (ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    const wsUrl = `ws://localhost:8000/ws/${sessionId.value}`
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      console.log('WebSocket connected:', sessionId.value)
    }

    ws.value.onmessage = (event) => {
      const message = JSON.parse(event.data)
      if (message.task_id) {
        updateTask(message.task_id, {
          status: message.status,
          progress: message.progress,
          result_url: message.result_url,
          error_message: message.error_message,
        })
      }
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.value.onclose = () => {
      console.log('WebSocket closed')
      // 自动重连
      setTimeout(connectWebSocket, 3000)
    }
  }

  function disconnectWebSocket() {
    ws.value?.close()
    ws.value = null
  }

  return {
    sessionId,
    tasks,
    activeTasks,
    completedTasks,
    addTask,
    updateTask,
    removeTask,
    connectWebSocket,
    disconnectWebSocket,
  }
})
