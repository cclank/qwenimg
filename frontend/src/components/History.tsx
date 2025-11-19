/**
 * 历史记录组件
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Empty,
  Space,
  Button,
  Select,
  Row,
  Col,
  Spin,
  message,
  Pagination,
  Modal,
} from 'antd';
import {
  HistoryOutlined,
  ReloadOutlined,
  ClearOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { TaskCard } from './TaskCard';
import { generationAPI } from '@/services/api';
import { useAppStore } from '@/store';
import type { Task, TaskType, TaskStatus } from '@/types';

const { Option } = Select;

export const History: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [filterType, setFilterType] = useState<TaskType | ''>('');
  const [filterStatus, setFilterStatus] = useState<TaskStatus | ''>('');
  const sessionId = useAppStore((state) => state.sessionId);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await generationAPI.getTasks({
        page,
        page_size: pageSize,
        task_type: filterType || undefined,
        status: filterStatus || undefined,
        session_id: sessionId,
      });

      setTasks(response.tasks);
      setTotal(response.total);
    } catch (error) {
      message.error('加载历史记录失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [page, filterType, filterStatus, sessionId]);

  const handleDelete = async (taskId: string) => {
    try {
      await generationAPI.deleteTask(taskId);
      message.success('已删除');
      fetchTasks();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleClearAll = () => {
    if (tasks.length === 0) {
      message.info('暂无记录可清空');
      return;
    }

    Modal.confirm({
      title: '确认清空历史记录',
      icon: <ExclamationCircleOutlined />,
      content: '确定要清空所有生成记录吗？此操作不可恢复。',
      okText: '确认清空',
      okType: 'danger',
      cancelText: '取消',
      centered: true,
      onOk: async () => {
        try {
          await generationAPI.clearTasks(sessionId);
          message.success('历史记录已清空');
          // 更新本地store
          useAppStore.getState().clearTasks();
          // 重新获取列表（应该是空的）
          fetchTasks();
        } catch (error) {
          message.error('清空失败');
        }
      },
    });
  };

  return (
    <Card
      title={
        <Space>
          <HistoryOutlined />
          <span>历史记录</span>
        </Space>
      }
      extra={
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchTasks}
            loading={loading}
          >
            刷新
          </Button>
          <Button
            icon={<ClearOutlined />}
            onClick={handleClearAll}
            danger
          >
            清空
          </Button>
        </Space>
      }
      bordered={false}
    >
      {/* 过滤器 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12}>
          <Select
            placeholder="筛选任务类型"
            style={{ width: '100%' }}
            value={filterType}
            onChange={setFilterType}
            allowClear
          >
            <Option value="">全部类型</Option>
            <Option value="text_to_image">文生图</Option>
            <Option value="image_to_video">图生视频</Option>
            <Option value="text_to_video">文生视频</Option>
          </Select>
        </Col>

        <Col xs={24} sm={12}>
          <Select
            placeholder="筛选任务状态"
            style={{ width: '100%' }}
            value={filterStatus}
            onChange={setFilterStatus}
            allowClear
          >
            <Option value="">全部状态</Option>
            <Option value="pending">等待中</Option>
            <Option value="running">生成中</Option>
            <Option value="completed">已完成</Option>
            <Option value="failed">失败</Option>
          </Select>
        </Col>
      </Row>

      {/* 任务列表 */}
      <Spin spinning={loading}>
        {tasks.length === 0 ? (
          <Empty
            description="暂无历史记录"
            style={{ padding: '40px 0' }}
          />
        ) : (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {tasks.map((task) => (
              <TaskCard key={task.task_id} task={task} onDelete={handleDelete} />
            ))}
          </Space>
        )}
      </Spin>

      {/* 分页 */}
      {total > pageSize && (
        <div style={{ marginTop: 24, textAlign: 'center' }}>
          <Pagination
            current={page}
            pageSize={pageSize}
            total={total}
            onChange={setPage}
            showSizeChanger={false}
            showTotal={(total) => `共 ${total} 条记录`}
          />
        </div>
      )}
    </Card>
  );
};
