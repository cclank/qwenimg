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
  const wsRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    // 处理WebSocket消息
    const handleMessage = (msg: WSMessage) => {
    switch (msg.type) {
      case 'connected':
        console.log('WebSocket已连接:', msg.session_id);
        break;

      case 'progress':
        // 更新任务进度
        if (msg.task_id && msg.data) {
          updateTask(msg.task_id, {
            progress: msg.data.progress,
            status: msg.data.status,
          });
        }
        break;

      case 'task_completed':
        // 任务完成
        if (msg.task_id && msg.data) {
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
          updateTask(msg.task_id, {
            status: 'failed',
            error_message: msg.data.error_message,
          });
          message.error(`任务失败: ${msg.data.error_message}`);
        }
        break;

      case 'pong':
        // 心跳响应
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
      unsubscribe();
      ws.disconnect();
    };
  }, [sessionId, updateTask]);

  return wsRef.current;
};
