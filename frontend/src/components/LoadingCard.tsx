/**
 * 生成中的占位卡片 - 显示进度和酷炫动画
 */
import React from 'react';
import { Task } from '@/types';
import './LoadingCard.css';

interface LoadingCardProps {
  task: Task;
}

export const LoadingCard: React.FC<LoadingCardProps> = ({ task }) => {
  const isVideo = task.task_type === 'text_to_video' || task.task_type === 'image_to_video';
  const progress = task.progress || 0;

  return (
    <div className="loading-card">
      <div className="loading-card-content">
        {/* 背景渐变动画 */}
        <div className="loading-bg-gradient" />

        {/* 图标 */}
        <div className="loading-icon">
          {isVideo ? (
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <rect x="2" y="3" width="20" height="18" rx="2" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M9 8L16 12L9 16V8Z" fill="currentColor"/>
            </svg>
          ) : (
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="1.5"/>
              <circle cx="8.5" cy="8.5" r="2.5" fill="currentColor"/>
              <path d="M3 16L7 12L11 16L16 11L21 16V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V16Z" fill="currentColor" fillOpacity="0.5"/>
            </svg>
          )}
        </div>

        {/* 进度百分比 */}
        <div className="loading-percentage">
          <span className="percentage-number">{Math.round(progress)}</span>
          <span className="percentage-symbol">%</span>
        </div>

        {/* 进度条 */}
        <div className="loading-progress-bar">
          <div
            className="loading-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* 状态文本 */}
        <div className="loading-status">
          {progress === 0 && '准备中...'}
          {progress > 0 && progress < 30 && '生成中...'}
          {progress >= 30 && progress < 70 && '渲染中...'}
          {progress >= 70 && progress < 100 && '即将完成...'}
          {progress === 100 && '处理完成'}
        </div>

        {/* 提示词预览 */}
        {task.prompt && (
          <div className="loading-prompt">
            {task.prompt.length > 60 ? `${task.prompt.slice(0, 60)}...` : task.prompt}
          </div>
        )}

        {/* 动画光效 */}
        <div className="loading-shimmer" />
      </div>
    </div>
  );
};
