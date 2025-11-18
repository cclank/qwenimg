/**
 * 主应用组件 - 简洁高级黑白灰设计
 */
import React, { useState, useEffect } from 'react';
import { Space, Button, Modal, Input, message, Typography, Dropdown, type MenuProps } from 'antd';
import {
  SettingOutlined,
  GithubOutlined,
  HistoryOutlined,
  BulbOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { CreationDialog } from './components/CreationDialog';
import { ActiveTasksPanel } from './components/ActiveTasksPanel';
import { History } from './components/History';
import { Inspiration } from './components/Inspiration';
import { useWebSocket } from './hooks/useWebSocket';
import { useAppStore } from './store';
import './App.css';

const { Text } = Typography;

type ViewMode = 'create' | 'history' | 'inspiration';

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('create');
  const [settingsVisible, setSettingsVisible] = useState(false);
  const apiKey = useAppStore((state) => state.apiKey);
  const setApiKey = useAppStore((state) => state.setApiKey);
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);
  const tasks = useAppStore((state) => state.tasks);

  // 初始化WebSocket
  useWebSocket();

  // 页面加载时获取历史任务
  useEffect(() => {
    const fetchHistoryTasks = async () => {
      try {
        const response = await fetch(`/api/generation/tasks?session_id=${sessionId}&page_size=20`);
        if (response.ok) {
          const data = await response.json();
          data.tasks.forEach((task: any) => {
            addTask({
              task_id: task.task_id,
              task_type: task.task_type,
              status: task.status,
              progress: task.progress,
              prompt: task.prompt,
              result_urls: task.result_urls,
              error_message: task.error_message,
              created_at: task.created_at,
              completed_at: task.completed_at,
            });
          });
        }
      } catch (error) {
        console.error('Failed to fetch history tasks:', error);
      }
    };

    fetchHistoryTasks();
  }, [sessionId, addTask]);

  const handleSaveSettings = (key: string) => {
    setApiKey(key);
    setSettingsVisible(false);
    message.success('设置已保存');
  };

  // 导航菜单
  const navMenuItems: MenuProps['items'] = [
    {
      key: 'create',
      label: '创作',
      onClick: () => setViewMode('create'),
    },
    {
      key: 'history',
      label: '历史',
      icon: <HistoryOutlined />,
      onClick: () => setViewMode('history'),
    },
    {
      key: 'inspiration',
      label: '灵感',
      icon: <BulbOutlined />,
      onClick: () => setViewMode('inspiration'),
    },
  ];

  // 获取进行中的任务数量
  const activeTasks = tasks.filter(
    (task) => task.status === 'pending' || task.status === 'running'
  );

  return (
    <div className="app-container">
      {/* 页面头部 */}
      <header className="app-header">
        <div className="app-logo">
          <div className="app-logo-icon">Q</div>
          <span className="app-logo-text">QwenImg</span>
        </div>

        <Space size="middle" className="app-nav">
          <Dropdown menu={{ items: navMenuItems }} placement="bottomRight">
            <Button
              type="text"
              style={{
                color: 'var(--color-text-secondary)',
                fontWeight: 500,
                borderRadius: 'var(--radius-md)',
              }}
            >
              {viewMode === 'create' && '创作'}
              {viewMode === 'history' && '历史'}
              {viewMode === 'inspiration' && '灵感'}
            </Button>
          </Dropdown>

          <Button
            type="text"
            icon={<SettingOutlined />}
            onClick={() => setSettingsVisible(true)}
            style={{
              color: 'var(--color-text-secondary)',
              borderRadius: 'var(--radius-md)',
            }}
          >
            设置
          </Button>

          <Button
            type="text"
            icon={<GithubOutlined />}
            href="https://github.com/cclank/qwenimg"
            target="_blank"
            style={{
              color: 'var(--color-text-secondary)',
              borderRadius: 'var(--radius-md)',
            }}
          >
            GitHub
          </Button>
        </Space>
      </header>

      {/* 主内容区域 */}
      <main className="app-main">
        {viewMode === 'create' && <CreationDialog />}
        {viewMode === 'history' && <History />}
        {viewMode === 'inspiration' && <Inspiration />}

        {/* 结果展示区域 */}
        {viewMode === 'create' && (
          <div className="results-masonry">
            {tasks
              .filter((task) => task.status === 'completed')
              .slice(0, 12)
              .map((task) => (
                <div key={task.task_id} style={{ breakInside: 'avoid', marginBottom: '16px' }}>
                  {task.task_type === 'text_to_image' && task.result_urls && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {task.result_urls.map((url, index) => (
                        <div
                          key={index}
                          style={{
                            borderRadius: 'var(--radius-lg)',
                            overflow: 'hidden',
                            boxShadow: 'var(--shadow-sm)',
                            transition: 'all 0.2s ease',
                            cursor: 'pointer',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                            e.currentTarget.style.transform = 'translateY(-2px)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                            e.currentTarget.style.transform = 'translateY(0)';
                          }}
                        >
                          <img
                            src={url}
                            alt={`Generated ${index}`}
                            style={{
                              width: '100%',
                              height: 'auto',
                              display: 'block',
                            }}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                  {(task.task_type === 'text_to_video' || task.task_type === 'image_to_video') &&
                    task.result_urls && (
                      <div
                        style={{
                          borderRadius: 'var(--radius-lg)',
                          overflow: 'hidden',
                          boxShadow: 'var(--shadow-sm)',
                          transition: 'all 0.2s ease',
                        }}
                      >
                        <video
                          src={task.result_urls[0]}
                          controls
                          style={{
                            width: '100%',
                            height: 'auto',
                            display: 'block',
                          }}
                        />
                      </div>
                    )}
                </div>
              ))}
          </div>
        )}
      </main>

      {/* 任务面板 - 仅在有活动任务时显示 */}
      {activeTasks.length > 0 && <ActiveTasksPanel />}

      {/* 设置对话框 */}
      <Modal
        title="设置"
        open={settingsVisible}
        onCancel={() => setSettingsVisible(false)}
        footer={null}
        centered
        styles={{
          mask: { backdropFilter: 'blur(4px)' },
        }}
      >
        <Space direction="vertical" style={{ width: '100%', padding: '16px 0' }} size="large">
          <div>
            <Text strong style={{ color: 'var(--color-text-primary)' }}>
              DashScope API Key
            </Text>
            <Input.Password
              placeholder="请输入你的API Key"
              defaultValue={apiKey}
              onPressEnter={(e) => handleSaveSettings((e.target as HTMLInputElement).value)}
              style={{ marginTop: 8, borderRadius: 'var(--radius-md)' }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              从{' '}
              <a
                href="https://dashscope.console.aliyun.com/apiKey"
                target="_blank"
                rel="noreferrer"
                style={{ color: 'var(--color-primary)' }}
              >
                阿里云控制台
              </a>{' '}
              获取
            </Text>
          </div>

          <div>
            <Text strong style={{ color: 'var(--color-text-primary)' }}>
              会话ID
            </Text>
            <Input
              value={sessionId}
              disabled
              style={{ marginTop: 8, borderRadius: 'var(--radius-md)' }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              用于WebSocket实时通信
            </Text>
          </div>

          <Button
            type="primary"
            onClick={() => {
              const input = document.querySelector('input[type="password"]') as HTMLInputElement;
              if (input) {
                handleSaveSettings(input.value);
              }
            }}
            block
            size="large"
            style={{
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-primary)',
              height: '44px',
            }}
          >
            保存设置
          </Button>
        </Space>
      </Modal>
    </div>
  );
}

export default App;
