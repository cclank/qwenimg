/**
 * 文生视频组件
 */
import React, { useState } from 'react';
import {
  Form,
  Input,
  Button,
  Select,
  InputNumber,
  Switch,
  Space,
  Card,
  Row,
  Col,
  message,
} from 'antd';
import { ThunderboltOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { generationAPI } from '@/services/api';
import { useAppStore } from '@/store';
import type { TextToVideoRequest } from '@/types';

const { TextArea } = Input;
const { Option } = Select;

export const TextToVideo: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);

      const request: TextToVideoRequest = {
        ...values,
        session_id: sessionId,
      };

      const response = await generationAPI.textToVideo(request);

      addTask({
        task_id: response.task_id,
        task_type: 'text_to_video',
        status: 'pending',
        progress: 0,
        prompt: values.prompt,
      });

      message.success('任务已创建，正在生成中...');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建任务失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title={
        <Space>
          <PlayCircleOutlined />
          <span>文生视频</span>
        </Space>
      }
      bordered={false}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          model: 'wan2.5-t2v-preview',
          resolution: '1080P',
          duration: 10,
          watermark: false,
        }}
      >
        <Row gutter={16}>
          <Col xs={24} lg={12}>
            <Form.Item
              label="场景描述"
              name="prompt"
              rules={[{ required: true, message: '请输入视频场景描述' }]}
            >
              <TextArea
                rows={5}
                placeholder="描述你想要生成的视频场景，例如：一只金色的小鸟在樱花树上跳跃，花瓣随风飘落，阳光透过树枝洒下斑驳的光影"
                showCount
                maxLength={1000}
              />
            </Form.Item>
          </Col>

          <Col xs={24} lg={12}>
            <Form.Item label="负面提示词" name="negative_prompt">
              <TextArea
                rows={5}
                placeholder="描述你不想要的元素，例如：低质量、模糊、抖动、噪点"
                showCount
                maxLength={500}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} sm={12} lg={8}>
            <Form.Item label="模型" name="model">
              <Select>
                <Option value="wan2.5-t2v-preview">万相 2.5 文生视频</Option>
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} sm={12} lg={8}>
            <Form.Item label="分辨率" name="resolution">
              <Select>
                <Option value="480P">480P</Option>
                <Option value="720P">720P</Option>
                <Option value="1080P">1080P</Option>
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} sm={12} lg={8}>
            <Form.Item label="时长" name="duration">
              <Select>
                <Option value={5}>5秒</Option>
                <Option value={10}>10秒</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item label="随机种子" name="seed">
              <InputNumber
                min={0}
                max={4294967290}
                style={{ width: '100%' }}
                placeholder="可选，用于复现相同结果"
              />
            </Form.Item>
          </Col>

          <Col xs={24} sm={12}>
            <Form.Item label="添加水印" name="watermark" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<ThunderboltOutlined />}
            size="large"
            block
          >
            {loading ? '创建中...' : '开始生成'}
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};
