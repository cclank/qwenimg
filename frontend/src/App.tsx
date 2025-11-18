/**
 * 主应用组件
 */
import React, { useState, useEffect } from 'react';
import {
  Layout,
  Menu,
  Typography,
  Space,
  Button,
  Modal,
  Input,
  message,
  Row,
  Col,
} from 'antd';
import {
  PictureOutlined,
  VideoCameraOutlined,
  PlayCircleOutlined,
  HistoryOutlined,
  BulbOutlined,
  SettingOutlined,
  GithubOutlined,
} from '@ant-design/icons';
import { TextToImage } from './components/TextToImage';
import { ImageToVideo } from './components/ImageToVideo';
import { TextToVideo } from './components/TextToVideo';
import { History } from './components/History';
import { Inspiration } from './components/Inspiration';
import { ActiveTasksPanel } from './components/ActiveTasksPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { useAppStore } from './store';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

function App() {
  const [activeKey, setActiveKey] = useState('text_to_image');
  const [settingsVisible, setSettingsVisible] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const apiKey = useAppStore((state) => state.apiKey);
  const setApiKey = useAppStore((state) => state.setApiKey);
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);

  // 初始化WebSocket
  useWebSocket();

  // 页面加载时获取历史任务
  useEffect(() => {
    const fetchHistoryTasks = async () => {
      try {
        const response = await fetch(`/api/generation/tasks?session_id=${sessionId}&page_size=20`);
        if (response.ok) {
          const data = await response.json();
          // 将历史任务添加到状态中（避免重复添加）
          data.tasks.forEach((task: any) => {
            // 检查任务是否已存在
            // 注意：这里简化处理，实际应该检查任务ID是否已存在
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

  const renderContent = () => {
    switch (activeKey) {
      case 'text_to_image':
        return <TextToImage />;
      case 'image_to_video':
        return <ImageToVideo />;
      case 'text_to_video':
        return <TextToVideo />;
      case 'history':
        return <History />;
      case 'inspiration':
        return <Inspiration />;
      default:
        return <TextToImage />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部导航 */}
      <Header
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Space size="large">
          <Title
            level={3}
            style={{
              margin: 0,
              color: '#fff',
              fontWeight: 'bold',
              letterSpacing: 1,
            }}
          >
            QwenImg AI 创作平台
          </Title>
          <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12 }}>
            阿里云通义万相多模态AI
          </Text>
        </Space>

        <Space>
          <Button
            type="text"
            icon={<SettingOutlined />}
            onClick={() => setSettingsVisible(true)}
            style={{ color: '#fff' }}
          >
            设置
          </Button>
          <Button
            type="text"
            icon={<GithubOutlined />}
            href="https://github.com/cclank/qwenimg"
            target="_blank"
            style={{ color: '#fff' }}
          >
            GitHub
          </Button>
        </Space>
      </Header>

      <Layout>
        {/* 左侧菜单 */}
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          width={200}
          style={{ background: '#fff' }}
        >
          <Menu
            mode="inline"
            selectedKeys={[activeKey]}
            onClick={({ key }) => setActiveKey(key)}
            style={{ height: '100%', borderRight: 0 }}
            items={[
              {
                key: 'generation',
                label: '创作工具',
                type: 'group',
                children: [
                  {
                    key: 'text_to_image',
                    icon: <PictureOutlined />,
                    label: '文生图',
                  },
                  {
                    key: 'image_to_video',
                    icon: <VideoCameraOutlined />,
                    label: '图生视频',
                  },
                  {
                    key: 'text_to_video',
                    icon: <PlayCircleOutlined />,
                    label: '文生视频',
                  },
                ],
              },
              {
                key: 'manage',
                label: '管理',
                type: 'group',
                children: [
                  {
                    key: 'history',
                    icon: <HistoryOutlined />,
                    label: '历史记录',
                  },
                  {
                    key: 'inspiration',
                    icon: <BulbOutlined />,
                    label: '灵感画廊',
                  },
                ],
              },
            ]}
          />
        </Sider>

        {/* 主内容区 */}
        <Layout style={{ padding: '24px' }}>
          <Content>
            <Row gutter={24}>
              {/* 左侧主区域 */}
              <Col xs={24} xl={16}>
                {renderContent()}
              </Col>

              {/* 右侧任务面板 */}
              <Col xs={24} xl={8}>
                <ActiveTasksPanel />
              </Col>
            </Row>
          </Content>
        </Layout>
      </Layout>

      {/* 设置对话框 */}
      <Modal
        title="设置"
        open={settingsVisible}
        onCancel={() => setSettingsVisible(false)}
        footer={null}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>DashScope API Key</Text>
            <Input.Password
              placeholder="请输入你的API Key"
              defaultValue={apiKey}
              onPressEnter={(e) =>
                handleSaveSettings((e.target as HTMLInputElement).value)
              }
              style={{ marginTop: 8 }}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              从{' '}
              <a
                href="https://dashscope.console.aliyun.com/apiKey"
                target="_blank"
                rel="noreferrer"
              >
                阿里云控制台
              </a>{' '}
              获取
            </Text>
          </div>

          <div>
            <Text strong>会话ID</Text>
            <Input value={sessionId} disabled style={{ marginTop: 8 }} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              用于WebSocket实时通信
            </Text>
          </div>

          <Button
            type="primary"
            onClick={() => {
              const input = document.querySelector(
                'input[type="password"]'
              ) as HTMLInputElement;
              if (input) {
                handleSaveSettings(input.value);
              }
            }}
            block
          >
            保存设置
          </Button>
        </Space>
      </Modal>
    </Layout>
  );
}

export default App;
