/**
 * 任务卡片组件 - 显示任务状态和结果
 */
import React from 'react';
import { Card, Progress, Image, Tag, Space, Button, Typography } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import type { Task } from '@/types';
import dayjs from 'dayjs';

const { Text, Paragraph } = Typography;

interface TaskCardProps {
  task: Task;
  onDelete?: (taskId: string) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onDelete }) => {
  const getStatusTag = () => {
    switch (task.status) {
      case 'pending':
        return (
          <Tag icon={<ClockCircleOutlined />} color="default">
            等待中
          </Tag>
        );
      case 'running':
        return (
          <Tag icon={<LoadingOutlined />} color="processing">
            生成中
          </Tag>
        );
      case 'completed':
        return (
          <Tag icon={<CheckCircleOutlined />} color="success">
            已完成
          </Tag>
        );
      case 'failed':
        return (
          <Tag icon={<CloseCircleOutlined />} color="error">
            失败
          </Tag>
        );
      default:
        return null;
    }
  };

  const getTaskTypeLabel = () => {
    switch (task.task_type) {
      case 'text_to_image':
        return '文生图';
      case 'image_to_video':
        return '图生视频';
      case 'text_to_video':
        return '文生视频';
      default:
        return task.task_type;
    }
  };

  const handleDownload = (url: string, index: number) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = `result_${task.task_id}_${index}`;
    link.click();
  };

  return (
    <Card
      size="small"
      title={
        <Space>
          <Text strong>{getTaskTypeLabel()}</Text>
          {getStatusTag()}
        </Space>
      }
      extra={
        <Space>
          {task.created_at && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {dayjs(task.created_at).format('HH:mm:ss')}
            </Text>
          )}
          {onDelete && (
            <Button
              type="text"
              danger
              size="small"
              icon={<DeleteOutlined />}
              onClick={() => onDelete(task.task_id)}
            />
          )}
        </Space>
      }
    >
      {/* 提示词 */}
      {task.prompt && (
        <Paragraph
          ellipsis={{ rows: 2, expandable: true }}
          style={{ marginBottom: 12 }}
        >
          <Text type="secondary">提示词：</Text>
          {task.prompt}
        </Paragraph>
      )}

      {/* 进度条 */}
      {(task.status === 'pending' || task.status === 'running') && (
        <Progress
          percent={Math.round(task.progress)}
          status={task.status === 'running' ? 'active' : 'normal'}
          size="small"
        />
      )}

      {/* 错误信息 */}
      {task.status === 'failed' && task.error_message && (
        <Text type="danger" style={{ fontSize: 12 }}>
          错误：{task.error_message}
        </Text>
      )}

      {/* 结果展示 */}
      {task.status === 'completed' && task.result_urls && (
        <div style={{ marginTop: 12 }}>
          {task.task_type === 'text_to_image' ? (
            <Image.PreviewGroup>
              <Space wrap>
                {task.result_urls.map((url, index) => (
                  <div key={index} style={{ position: 'relative' }}>
                    <Image
                      src={url}
                      alt={`result-${index}`}
                      width={120}
                      height={120}
                      style={{ objectFit: 'cover', borderRadius: 4 }}
                    />
                    <Button
                      size="small"
                      icon={<DownloadOutlined />}
                      style={{
                        position: 'absolute',
                        bottom: 8,
                        right: 8,
                      }}
                      onClick={() => handleDownload(url, index)}
                    />
                  </div>
                ))}
              </Space>
            </Image.PreviewGroup>
          ) : (
            <Space direction="vertical" style={{ width: '100%' }}>
              {task.result_urls.map((url, index) => (
                <div key={index}>
                  <video
                    src={url}
                    controls
                    style={{ width: '100%', maxHeight: 300, borderRadius: 4 }}
                  />
                  <Button
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownload(url, index)}
                    style={{ marginTop: 8 }}
                  >
                    下载视频
                  </Button>
                </div>
              ))}
            </Space>
          )}
        </div>
      )}
    </Card>
  );
};
