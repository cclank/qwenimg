/**
 * WebSocket自定义Hook
 */
import { useEffect, useRef } from 'react';
import WebSocketService from '@/services/websocket';
import { useAppStore } from '@/store';
import type { WSMessage } from '@/types';
import { message } from 'antd';

export const useWebSocket = () => {
  const sessionId = useAppStore((state) => state.sessionId);
  const updateTask = useAppStore((state) => state.updateTask);
  const tasks = useAppStore((state) => state.tasks);
  const wsRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    console.log('Initializing WebSocket with session_id:', sessionId);

    // 处理WebSocket消息
    const handleMessage = (msg: WSMessage) => {
      console.log('Received WebSocket message:', msg);

      switch (msg.type) {
        case 'connected':
          console.log('WebSocket已连接:', msg.session_id);
          break;

        case 'progress':
          // 更新任务进度
          if (msg.task_id && msg.data) {
            console.log('Updating task progress:', msg.task_id, msg.data);
            updateTask(msg.task_id, {
              progress: msg.data.progress,
              status: msg.data.status,
            });
          }
          break;

        case 'task_completed':
          // 任务完成
          if (msg.task_id && msg.data) {
            console.log('Task completed:', msg.task_id, msg.data);
            updateTask(msg.task_id, {
              status: 'completed',
              progress: 100,
              result_urls: msg.data.result_urls,
            });
            message.success('任务完成！');
          }
          break;

        case 'task_failed':
          // 任务失败
          if (msg.task_id && msg.data) {
            console.log('Task failed:', msg.task_id, msg.data);
            updateTask(msg.task_id, {
              status: 'failed',
              error_message: msg.data.error_message,
            });
            message.error(`任务失败: ${msg.data.error_message}`);
          }
          break;

        case 'pong':
          // 心跳响应
          console.log('Received pong message');
          break;

        default:
          console.log('Unknown message type:', msg.type);
      }
    };

    // 创建WebSocket连接
    const ws = new WebSocketService(sessionId);
    wsRef.current = ws;

    // 订阅消息
    const unsubscribe = ws.onMessage(handleMessage);

    // 连接
    ws.connect();

    // 清理
    return () => {
      console.log('Cleaning up WebSocket connection');
      unsubscribe();
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, [sessionId, updateTask]);

  // 添加任务状态轮询机制
  useEffect(() => {
    // 只对进行中的任务进行轮询
    const activeTasks = tasks.filter(task =>
      task.status === 'pending' || task.status === 'running'
    );

    if (activeTasks.length === 0) return;

    // 每5秒轮询一次任务状态
    const interval = setInterval(async () => {
      for (const task of activeTasks) {
        try {
          const response = await fetch(`/api/generation/task/${task.task_id}`);
          if (response.ok) {
            const taskData = await response.json();
            // 如果任务已完成且前端状态未更新，则更新状态
            if (
              (taskData.status === 'completed' && task.status !== 'completed') ||
              (taskData.status === 'failed' && task.status !== 'failed')
            ) {
              updateTask(task.task_id, {
                status: taskData.status,
                progress: taskData.progress,
                result_urls: taskData.result_urls,
                error_message: taskData.error_message,
              });

              if (taskData.status === 'completed') {
                message.success('任务完成！');
              } else if (taskData.status === 'failed') {
                message.error(`任务失败: ${taskData.error_message}`);
              }
            }
          }
        } catch (error) {
          console.error('Failed to poll task status:', error);
        }
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [tasks, updateTask]);

  return wsRef.current;
};
