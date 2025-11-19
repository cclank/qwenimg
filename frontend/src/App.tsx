/**
 * 主应用组件 - 简洁高级黑白灰设计
 */
import React, { useState, useEffect } from 'react';
import { Space, Button, Modal, Input, message, Typography, Dropdown, Image, Checkbox, type MenuProps } from 'antd';
import {
  SettingOutlined,
  GithubOutlined,
  HistoryOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  PictureOutlined,
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
  const setImageToVideoUrl = useAppStore((state) => state.setImageToVideoUrl);

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
              image_count: task.image_count,
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

  // 下载图片或视频
  const handleDownload = async (url: string, filename?: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename || url.split('/').pop() || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
      message.success('下载成功');
    } catch (error) {
      message.error('下载失败');
    }
  };

  // 图片再创作 - 加载到图生视频
  const handleImageToVideo = (imageUrl: string) => {
    setImageToVideoUrl(imageUrl);
    message.success('图片已加载到图生视频');
  };

  // 删除任务
  const handleDeleteTask = (taskId: string, url?: string) => {
    const skipConfirm = useAppStore.getState().skipDeleteConfirm;
    const setSkipDeleteConfirm = useAppStore.getState().setSkipDeleteConfirm;

    const executeDelete = async () => {
      try {
        let apiUrl = `/api/generation/task/${taskId}`;
        if (url) {
          apiUrl += `?url=${encodeURIComponent(url)}`;
        }

        const response = await fetch(apiUrl, {
          method: 'DELETE',
        });

        if (response.ok) {
          if (url) {
            useAppStore.getState().removeTaskResult(taskId, url);
          } else {
            useAppStore.getState().removeTask(taskId);
          }
          message.success('删除成功');
        } else {
          message.error('删除失败');
        }
      } catch (error) {
        console.error('Failed to delete task:', error);
        message.error('删除出错');
      }
    };

    if (skipConfirm) {
      executeDelete();
      return;
    }

    let dontAskAgain = false;

    Modal.confirm({
      title: '确认删除',
      content: (
        <div>
          <p>{url ? '确定要删除这张图片吗？' : '确定要删除这个生成任务吗？删除后无法恢复。'}</p>
          <div style={{ marginTop: '12px' }}>
            <Checkbox onChange={(e) => { dontAskAgain = e.target.checked; }}>
              不再提示
            </Checkbox>
          </div>
        </div>
      ),
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      centered: true,
      onOk: () => {
        if (dontAskAgain) {
          setSkipDeleteConfirm(true);
        }
        return executeDelete();
      },
    });
  };

  // 导航菜单
  const navMenuItems: MenuProps['items'] = [
    {
      key: 'create',
      label: '创作',
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
        <div
          className="app-logo"
          onClick={() => setViewMode('create')}
          style={{ cursor: 'pointer' }}
        >
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
            {/* 先显示正在生成的任务（LoadingCard） - 拆分为多个卡片 */}
            {tasks
              .filter((task) => task.status === 'pending' || task.status === 'running')
              .sort((a, b) => {
                const timeA = new Date(a.created_at || 0).getTime();
                const timeB = new Date(b.created_at || 0).getTime();
                return timeB - timeA;
              })
              .flatMap((task) => {
                // 如果是文生图且有数量设置，渲染对应数量的卡片
                const count = task.task_type === 'text_to_image' ? (task.image_count || 1) : 1;
                return Array.from({ length: count }).map((_, index) => (
                  <div key={`${task.task_id}-${index}`} style={{ breakInside: 'avoid', width: 'calc(20% - 16px)' }}>
                    <LoadingCard task={task} />
                  </div>
                ));
              })}

            {/* 然后显示已完成的任务 - 拆分为多个卡片 */}
            {tasks
              .filter((task) => task.status === 'completed')
              .sort((a, b) => {
                // 按创建时间倒序排序（最新的在前）
                const timeA = new Date(a.created_at || 0).getTime();
                const timeB = new Date(b.created_at || 0).getTime();
                return timeB - timeA;
              })
              .flatMap((task) => {
                // 文生图：每个结果一个卡片
                if (task.task_type === 'text_to_image' && Array.isArray(task.result_urls) && task.result_urls.length > 0) {
                  return task.result_urls.map((url, index) => (
                    <div key={`${task.task_id}-${index}`} style={{ breakInside: 'avoid', width: 'calc(20% - 16px)' }}>
                      <div className="result-card">
                        <Image
                          src={url}
                          alt={task.prompt || `Generated ${index}`}
                          style={{
                            width: '100%',
                            height: 'auto',
                            display: 'block',
                            maxHeight: '450px',
                            objectFit: 'cover',
                            cursor: 'grab',
                          }}
                          draggable="true"
                          onDragStart={(e) => {
                            e.dataTransfer.setData('text/plain', url);
                            e.dataTransfer.setData('text/uri-list', url);
                            e.dataTransfer.effectAllowed = 'copy';
                          }}
                          preview={{
                            mask: (
                              <div style={{ fontSize: '14px' }}>
                                点击预览
                              </div>
                            ),
                            toolbarRender: (_, { transform: { scale }, actions: { onZoomOut, onZoomIn, onRotateLeft, onRotateRight } }) => (
                              <Space size={12} className="toolbar-wrapper">
                                <Button
                                  type="primary"
                                  icon={<DownloadOutlined />}
                                  onClick={() => handleDownload(url)}
                                >
                                  下载
                                </Button>
                                <Button
                                  icon={<PictureOutlined />}
                                  onClick={() => {
                                    handleImageToVideo(url);
                                  }}
                                >
                                  图生视频
                                </Button>
                              </Space>
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
                                      background: 'rgba(0, 0, 0, 0.6)',
                                      backdropFilter: 'blur(10px)',
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
                          <div className="prompt-tooltip">
                            {task.prompt}
                          </div>
                        )}
                        <div
                          style={{
                            position: 'absolute',
                            top: '8px',
                            left: '8px',
                            background: 'rgba(0, 0, 0, 0.6)',
                            backdropFilter: 'blur(4px)',
                            borderRadius: 'var(--radius-full)',
                            padding: '4px 8px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            zIndex: 10,
                            fontSize: '11px',
                            fontWeight: 500,
                            color: 'white',
                            opacity: 0,
                            transition: 'opacity 0.2s ease',
                            pointerEvents: 'none',
                          }}
                          className="drag-indicator"
                        >
                          <div style={{
                            width: '6px',
                            height: '10px',
                            border: '1px dotted white',
                            borderRadius: '2px',
                            opacity: 0.8
                          }} />
                          <span>拖拽创作</span>
                        </div>
                        {/* 删除按钮 */}
                        <div
                          className="delete-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteTask(task.task_id);
                          }}
                          style={{
                            position: 'absolute',
                            top: '8px',
                            right: '8px',
                            background: 'rgba(0, 0, 0, 0.6)',
                            backdropFilter: 'blur(4px)',
                            borderRadius: 'var(--radius-full)',
                            width: '28px',
                            height: '28px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 10,
                            color: 'white',
                            cursor: 'pointer',
                            opacity: 0,
                            transition: 'all 0.2s ease',
                          }}
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  ));
                }

                // 视频任务：每个结果一个卡片（通常只有一个）
                if ((task.task_type === 'text_to_video' || task.task_type === 'image_to_video') &&
                  Array.isArray(task.result_urls) && task.result_urls.length > 0) {
                  return task.result_urls.map((url, index) => (
                    <div key={`${task.task_id}-${index}`} style={{ breakInside: 'avoid', width: 'calc(20% - 16px)' }}>
                      <div
                        className="result-card"
                        onClick={() => setVideoPreview({ visible: true, url: url, prompt: task.prompt })}
                      >
                        {/* Video Badge - Distinguish from images */}
                        <div
                          style={{
                            position: 'absolute',
                            top: '8px',
                            right: '8px',
                            background: 'rgba(0, 0, 0, 0.6)',
                            backdropFilter: 'blur(4px)',
                            borderRadius: 'var(--radius-full)',
                            padding: '6px 12px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            zIndex: 10,
                            fontSize: '12px',
                            fontWeight: 500,
                            color: 'white',
                            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                          }}
                        >
                          <PlayCircleOutlined style={{ fontSize: '14px' }} />
                          <span>视频</span>
                        </div>
                        {/* 删除按钮 - 视频 */}
                        <div
                          className="delete-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteTask(task.task_id);
                          }}
                          style={{
                            position: 'absolute',
                            top: '8px',
                            right: '74px', // 避开视频Badge
                            background: 'rgba(0, 0, 0, 0.6)',
                            backdropFilter: 'blur(4px)',
                            borderRadius: 'var(--radius-full)',
                            width: '28px',
                            height: '28px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 10,
                            color: 'white',
                            cursor: 'pointer',
                            opacity: 0,
                            transition: 'all 0.2s ease',
                          }}
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" />
                          </svg>
                        </div>
                        <video
                          src={url}
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
                            backdropFilter: 'blur(4px)',
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
                          <div className="prompt-tooltip">
                            {task.prompt}
                          </div>
                        )}
                      </div>
                    </div>
                  ));
                }

                return [];
              })}
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
        footer={
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => handleDownload(videoPreview.url)}
            >
              下载视频
            </Button>
          </div>
        }
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
