/**
 * 实时任务面板 - 显示当前进行中的任务
 */
import React from 'react';
import { Card, Empty, Space, Badge } from 'antd';
import { RocketOutlined } from '@ant-design/icons';
import { useAppStore } from '@/store';
import { TaskCard } from './TaskCard';

export const ActiveTasksPanel: React.FC = () => {
  const tasks = useAppStore((state) => state.tasks);
  const removeTask = useAppStore((state) => state.removeTask);

  // 只显示进行中和等待中的任务
  const activeTasks = tasks.filter(
    (task) => task.status === 'pending' || task.status === 'running'
  );

  // 最近完成的任务（最多3个）
  const recentCompleted = tasks
    .filter((task) => task.status === 'completed' || task.status === 'failed')
    .slice(0, 3);

  const allDisplayTasks = [...activeTasks, ...recentCompleted];

  return (
    <Card
      title={
        <Space>
          <RocketOutlined />
          <span>当前任务</span>
          {activeTasks.length > 0 && (
            <Badge count={activeTasks.length} showZero />
          )}
        </Space>
      }
      bordered={false}
      size="small"
    >
      {allDisplayTasks.length === 0 ? (
        <Empty
          description="暂无进行中的任务"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          style={{ padding: '20px 0' }}
        />
      ) : (
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {allDisplayTasks.map((task) => (
            <TaskCard
              key={task.task_id}
              task={task}
              onDelete={removeTask}
            />
          ))}
        </Space>
      )}
    </Card>
  );
};
