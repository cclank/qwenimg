/**
 * 灵感画廊组件 - 激发用户创作
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Tag,
  Space,
  Button,
  Typography,
  Empty,
  Spin,
  message,
  Tabs,
} from 'antd';
import {
  BulbOutlined,
  LikeOutlined,
  CopyOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { inspirationAPI } from '@/services/api';
import type { Inspiration as InspirationType } from '@/types';

const { Text, Paragraph } = Typography;

export const Inspiration: React.FC = () => {
  const [inspirations, setInspirations] = useState<InspirationType[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>('');

  const fetchInspirations = async (category?: string) => {
    try {
      setLoading(true);
      const response = await inspirationAPI.getList({
        category,
        limit: 50,
      });

      setInspirations(response.inspirations);
      setCategories(response.categories);
    } catch (error) {
      message.error('加载灵感失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspirations(activeCategory || undefined);
  }, [activeCategory]);

  const handleLike = async (id: number) => {
    try {
      await inspirationAPI.like(id);
      // 更新点赞数
      setInspirations((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, likes: item.likes + 1 } : item
        )
      );
      message.success('点赞成功');
    } catch (error) {
      message.error('点赞失败');
    }
  };

  const handleCopyPrompt = (prompt: string) => {
    navigator.clipboard.writeText(prompt);
    message.success('提示词已复制到剪贴板');
  };

  const getTaskTypeLabel = (taskType: string) => {
    switch (taskType) {
      case 'text_to_image':
        return '文生图';
      case 'image_to_video':
        return '图生视频';
      case 'text_to_video':
        return '文生视频';
      default:
        return taskType;
    }
  };

  const getTaskTypeColor = (taskType: string) => {
    switch (taskType) {
      case 'text_to_image':
        return 'blue';
      case 'image_to_video':
        return 'purple';
      case 'text_to_video':
        return 'orange';
      default:
        return 'default';
    }
  };

  return (
    <Card
      title={
        <Space>
          <BulbOutlined />
          <span>创作灵感</span>
        </Space>
      }
      bordered={false}
    >
      <Tabs
        activeKey={activeCategory}
        onChange={setActiveCategory}
        type="card"
        items={[
          { key: '', label: '全部' },
          ...categories.map((cat) => ({ key: cat, label: cat })),
        ]}
      />

      <Spin spinning={loading}>
        {inspirations.length === 0 ? (
          <Empty description="暂无灵感示例" style={{ padding: '40px 0' }} />
        ) : (
          <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
            {inspirations.map((item) => (
              <Col xs={24} sm={12} lg={8} xl={6} key={item.id}>
                <Card
                  hoverable
                  size="small"
                  cover={
                    item.thumbnail_url && (
                      <div
                        style={{
                          height: 180,
                          background: `url(${item.thumbnail_url}) center/cover`,
                          borderRadius: '4px 4px 0 0',
                        }}
                      />
                    )
                  }
                  actions={[
                    <Button
                      type="text"
                      icon={<LikeOutlined />}
                      onClick={() => handleLike(item.id)}
                    >
                      {item.likes}
                    </Button>,
                    <Button
                      type="text"
                      icon={<CopyOutlined />}
                      onClick={() => handleCopyPrompt(item.prompt)}
                    >
                      复制
                    </Button>,
                    <Button type="text" icon={<ThunderboltOutlined />}>
                      使用
                    </Button>,
                  ]}
                >
                  <Card.Meta
                    title={
                      <Space>
                        <Text strong ellipsis style={{ maxWidth: 150 }}>
                          {item.title}
                        </Text>
                        <Tag color={getTaskTypeColor(item.task_type)}>
                          {getTaskTypeLabel(item.task_type)}
                        </Tag>
                      </Space>
                    }
                    description={
                      <div>
                        <Paragraph
                          ellipsis={{ rows: 3 }}
                          style={{ fontSize: 12, marginBottom: 8 }}
                        >
                          {item.prompt}
                        </Paragraph>
                        {item.tags && item.tags.length > 0 && (
                          <Space size={4} wrap>
                            {item.tags.map((tag, index) => (
                              <Tag key={index} style={{ fontSize: 10 }}>
                                {tag}
                              </Tag>
                            ))}
                          </Space>
                        )}
                      </div>
                    }
                  />
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Spin>
    </Card>
  );
};
