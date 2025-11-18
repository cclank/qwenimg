/**
 * 进度模拟Hook - 在后端没有实时进度时模拟进度增长
 */
import { useEffect, useRef } from 'react';
import { useAppStore } from '@/store';
import type { Task } from '@/types';

// 进度模拟配置
const PROGRESS_CONFIG = {
  text_to_image: {
    duration: 30000, // 30秒
    maxProgress: 90, // 最大模拟到90%
  },
  text_to_video: {
    duration: 180000, // 3分钟
    maxProgress: 90,
  },
  image_to_video: {
    duration: 180000, // 3分钟
    maxProgress: 90,
  },
};

export const useProgressSimulation = () => {
  const tasks = useAppStore((state) => state.tasks);
  const updateTask = useAppStore((state) => state.updateTask);
  const simulationTimers = useRef<Map<string, number>>(new Map());

  useEffect(() => {
    // 查找需要模拟进度的任务（pending或running，且progress < 10）
    const tasksNeedingSimulation = tasks.filter(
      (task) =>
        (task.status === 'pending' || task.status === 'running') &&
        (task.progress || 0) < 10
    );

    tasksNeedingSimulation.forEach((task) => {
      // 如果这个任务已经在模拟中，跳过
      if (simulationTimers.current.has(task.task_id)) {
        return;
      }

      const config = PROGRESS_CONFIG[task.task_type];
      if (!config) return;

      const startTime = Date.now();
      const startProgress = task.progress || 0;

      // 创建模拟定时器
      const timerId = window.setInterval(() => {
        const elapsed = Date.now() - startTime;
        const progressRatio = Math.min(elapsed / config.duration, 1);

        // 使用缓动函数（easeOutCubic）让进度增长更自然
        const easeProgress = 1 - Math.pow(1 - progressRatio, 3);
        const simulatedProgress = Math.min(
          startProgress + (config.maxProgress - startProgress) * easeProgress,
          config.maxProgress
        );

        // 更新任务进度
        updateTask(task.task_id, {
          progress: Math.round(simulatedProgress),
          status: simulatedProgress > 5 ? 'running' : task.status,
        });

        // 如果达到最大进度，停止模拟
        if (simulatedProgress >= config.maxProgress) {
          clearInterval(timerId);
          simulationTimers.current.delete(task.task_id);
        }
      }, 500); // 每500ms更新一次

      simulationTimers.current.set(task.task_id, timerId);
    });

    // 清理已完成或失败任务的定时器
    simulationTimers.current.forEach((timerId, taskId) => {
      const task = tasks.find((t) => t.task_id === taskId);
      if (!task || task.status === 'completed' || task.status === 'failed') {
        clearInterval(timerId);
        simulationTimers.current.delete(taskId);
      }
    });

    // 组件卸载时清理所有定时器
    return () => {
      simulationTimers.current.forEach((timerId) => clearInterval(timerId));
      simulationTimers.current.clear();
    };
  }, [tasks, updateTask]);
};
