/**
 * 主应用组件 - 简洁高级黑白灰设计
 */
import React, { useState, useEffect } from 'react';
import { Space, Button, Modal, Input, message, Typography, Dropdown, Image, type MenuProps } from 'antd';
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
import { LoadingCard } from './components/LoadingCard';
import { useWebSocket } from './hooks/useWebSocket';
import { useProgressSimulation } from './hooks/useProgressSimulation';
import { useAppStore } from './store';
import './App.css';

const { Text } = Typography;

type ViewMode = 'create' | 'history' | 'inspiration';

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('create');
  const [settingsVisible, setSettingsVisible] = useState(false);
  const [videoPreview, setVideoPreview] = useState<{ visible: boolean; url: string; prompt?: string }>({
    visible: false,
    url: '',
  });
  const apiKey = useAppStore((state) => state.apiKey);
  const setApiKey = useAppStore((state) => state.setApiKey);
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);
  const tasks = useAppStore((state) => state.tasks);

  // 初始化WebSocket
  useWebSocket();

  // 初始化进度模拟
  useProgressSimulation();

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
      label: '历史记录',
      icon: <HistoryOutlined />,
      onClick: () => setViewMode('history'),
    },
    {
      key: 'inspiration',
      label: '灵感画廊',
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

        {viewMode === 'history' && (
          <div>
            <Button
              onClick={() => setViewMode('create')}
              style={{
                marginBottom: '16px',
                borderRadius: 'var(--radius-md)',
              }}
            >
              返回创作
            </Button>
            <History />
          </div>
        )}

        {viewMode === 'inspiration' && (
          <div>
            <Button
              onClick={() => setViewMode('create')}
              style={{
                marginBottom: '16px',
                borderRadius: 'var(--radius-md)',
              }}
            >
              返回创作
            </Button>
            <Inspiration />
          </div>
        )}

        {/* 结果展示区域 - 最新的在前面 */}
        {viewMode === 'create' && (
          <div className="results-masonry">
            {/* 先显示正在生成的任务（LoadingCard） */}
            {tasks
              .filter((task) => task.status === 'pending' || task.status === 'running')
              .sort((a, b) => {
                const timeA = new Date(a.created_at || 0).getTime();
                const timeB = new Date(b.created_at || 0).getTime();
                return timeB - timeA;
              })
              .map((task) => (
                <div key={task.task_id} style={{ breakInside: 'avoid', width: 'calc(20% - 16px)' }}>
                  <LoadingCard task={task} />
                </div>
              ))}

            {/* 然后显示已完成的任务 */}
            {tasks
              .filter((task) => task.status === 'completed')
              .sort((a, b) => {
                // 按创建时间倒序排序（最新的在前）
                const timeA = new Date(a.created_at || 0).getTime();
                const timeB = new Date(b.created_at || 0).getTime();
                return timeB - timeA;
              })
              .map((task) => (
                <div key={task.task_id} style={{ breakInside: 'avoid', width: 'calc(20% - 16px)' }}>
                  {task.task_type === 'text_to_image' && task.result_urls && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <Image.PreviewGroup>
                        {task.result_urls.map((url, index) => (
                          <div
                            key={index}
                            style={{
                              borderRadius: 'var(--radius-lg)',
                              overflow: 'hidden',
                              boxShadow: 'var(--shadow-sm)',
                              transition: 'all 0.2s ease',
                              position: 'relative',
                              width: '100%',
                              height: '100%',
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
                            <Image
                              src={url}
                              alt={task.prompt || `Generated ${index}`}
                              style={{
                                width: '100%',
                                height: 'auto',
                                display: 'block',
                                maxHeight: '450px',
                                objectFit: 'cover',
                                cursor: 'pointer',
                              }}
                              preview={{
                                mask: (
                                  <div style={{ fontSize: '14px' }}>
                                    点击预览
                                  </div>
                                ),
                                imageRender: (originalNode) => (
                                  <div style={{ position: 'relative' }}>
                                    {originalNode}
                                    {task.prompt && (
                                      <div
                                        style={{
                                          position: 'absolute',
                                          bottom: 0,
                                          left: 0,
                                          right: 0,
                                          background: 'rgba(0, 0, 0, 0.8)',
                                          color: 'white',
                                          padding: '16px 24px',
                                          fontSize: '14px',
                                          lineHeight: '1.6',
                                        }}
                                      >
                                        <strong>提示词：</strong>{task.prompt}
                                      </div>
                                    )}
                                  </div>
                                ),
                              }}
                            />
                            {task.prompt && (
                              <div
                                style={{
                                  position: 'absolute',
                                  bottom: 0,
                                  left: 0,
                                  right: 0,
                                  background: 'rgba(0, 0, 0, 0.7)',
                                  color: 'white',
                                  padding: '8px',
                                  fontSize: '12px',
                                  transform: 'translateY(100%)',
                                  transition: 'transform 0.2s ease',
                                }}
                                className="prompt-tooltip"
                              >
                                {task.prompt}
                              </div>
                            )}
                          </div>
                        ))}
                      </Image.PreviewGroup>
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
                          position: 'relative',
                          cursor: 'pointer',
                          width: '100%',
                          aspectRatio: '1',
                          background: '#000',
                        }}
                        onClick={() => setVideoPreview({ visible: true, url: task.result_urls[0], prompt: task.prompt })}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                          e.currentTarget.style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                          e.currentTarget.style.transform = 'translateY(0)';
                        }}
                      >
                        <video
                          src={task.result_urls[0]}
                          style={{
                            width: '100%',
                            height: '100%',
                            display: 'block',
                            objectFit: 'contain',
                            pointerEvents: 'none',
                          }}
                        />
                        <div
                          style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            background: 'rgba(0, 0, 0, 0.6)',
                            color: 'white',
                            padding: '12px 24px',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '14px',
                            opacity: 0,
                            transition: 'opacity 0.2s ease',
                            pointerEvents: 'none',
                          }}
                          className="video-play-hint"
                        >
                          点击播放
                        </div>
                        {task.prompt && (
                          <div
                            style={{
                              position: 'absolute',
                              bottom: 0,
                              left: 0,
                              right: 0,
                              background: 'rgba(0, 0, 0, 0.7)',
                              color: 'white',
                              padding: '8px',
                              fontSize: '12px',
                              transform: 'translateY(100%)',
                              transition: 'transform 0.2s ease',
                            }}
                            className="prompt-tooltip"
                          >
                            {task.prompt}
                          </div>
                        )}
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

      {/* 视频预览对话框 */}
      <Modal
        title="视频预览"
        open={videoPreview.visible}
        onCancel={() => setVideoPreview({ visible: false, url: '' })}
        footer={null}
        centered
        width="80%"
        styles={{
          mask: { backdropFilter: 'blur(8px)' },
          body: { padding: 0 },
        }}
      >
        <div style={{ position: 'relative' }}>
          <video
            src={videoPreview.url}
            controls
            autoPlay
            style={{
              width: '100%',
              height: 'auto',
              display: 'block',
              borderRadius: 'var(--radius-md)',
            }}
          />
          {videoPreview.prompt && (
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                background: 'rgba(0, 0, 0, 0.8)',
                color: 'white',
                padding: '16px 24px',
                fontSize: '14px',
                lineHeight: '1.6',
                borderBottomLeftRadius: 'var(--radius-md)',
                borderBottomRightRadius: 'var(--radius-md)',
              }}
            >
              <strong>提示词：</strong>{videoPreview.prompt}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}

export default App;
