/**
 * 实时任务面板 - 浮动面板显示当前进行中的任务（默认最小化）
 */
import React, { useState } from 'react';
import { Empty, Space, Badge } from 'antd';
import { RocketOutlined, UpOutlined, DownOutlined } from '@ant-design/icons';
import { useAppStore } from '@/store';
import { TaskCard } from './TaskCard';

export const ActiveTasksPanel: React.FC = () => {
  const [collapsed, setCollapsed] = useState(true); // 默认最小化
  const tasks = useAppStore((state) => state.tasks);
  const removeTask = useAppStore((state) => state.removeTask);

  // 只显示进行中和等待中的任务
  const activeTasks = tasks.filter(
    (task) => task.status === 'pending' || task.status === 'running'
  );

  // 最近完成的任务（最多2个）
  const recentCompleted = tasks
    .filter((task) => task.status === 'completed' || task.status === 'failed')
    .slice(0, 2);

  const allDisplayTasks = [...activeTasks, ...recentCompleted];

  // 如果没有任务，不显示面板
  if (allDisplayTasks.length === 0) {
    return null;
  }

  return (
    <div className={`tasks-panel ${collapsed ? 'collapsed' : 'expanded'}`}>
      <div
        className="tasks-panel-header"
        onClick={() => setCollapsed(!collapsed)}
        style={{ cursor: 'pointer' }}
      >
        <Space size="small">
          <RocketOutlined style={{ color: 'var(--color-text-primary)' }} />
          <span className="tasks-panel-title">当前任务</span>
          {activeTasks.length > 0 && (
            <Badge
              count={activeTasks.length}
              showZero
              style={{
                background: 'var(--color-primary)',
              }}
            />
          )}
        </Space>
        {collapsed ? <DownOutlined /> : <UpOutlined />}
      </div>

      {!collapsed && (
        <div className="tasks-panel-body">
          {allDisplayTasks.map((task) => (
            <TaskCard
              key={task.task_id}
              task={task}
              onDelete={removeTask}
            />
          ))}
        </div>
      )}
    </div>
  );
};
