/**
 * 文生图组件
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
import { ThunderboltOutlined, PictureOutlined } from '@ant-design/icons';
import { generationAPI } from '@/services/api';
import { useAppStore } from '@/store';
import type { TextToImageRequest } from '@/types';

const { TextArea } = Input;
const { Option } = Select;

export const TextToImage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);

      const request: TextToImageRequest = {
        ...values,
        session_id: sessionId,
      };

      const response = await generationAPI.textToImage(request);

      // 添加到任务列表
      addTask({
        task_id: response.task_id,
        task_type: 'text_to_image',
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
          <PictureOutlined />
          <span>文生图</span>
        </Space>
      }
      bordered={false}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          model: 'wan2.5-t2i-preview',
          n: 1,
          size: '1024*1024',
          watermark: false,
        }}
      >
        <Row gutter={16}>
          <Col xs={24} lg={12}>
            <Form.Item
              label="提示词"
              name="prompt"
              rules={[{ required: true, message: '请输入图片描述' }]}
            >
              <TextArea
                rows={4}
                placeholder="描述你想要生成的图片，例如：一只可爱的猫咪坐在窗台上，阳光洒在它的身上，温馨的画面"
                showCount
                maxLength={1000}
              />
            </Form.Item>
          </Col>

          <Col xs={24} lg={12}>
            <Form.Item label="负面提示词" name="negative_prompt">
              <TextArea
                rows={4}
                placeholder="描述你不想要的元素，例如：低质量、模糊、变形"
                showCount
                maxLength={500}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} sm={12} lg={6}>
            <Form.Item label="模型" name="model">
              <Select>
                <Option value="wan2.5-t2i-preview">万相 2.5 (最新)</Option>
                <Option value="wanx-v1">通义万相 V1</Option>
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Form.Item label="生成数量" name="n">
              <InputNumber min={1} max={4} style={{ width: '100%' }} />
            </Form.Item>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Form.Item label="图片尺寸" name="size">
              <Select>
                <Option value="1024*1024">1024×1024 (方形)</Option>
                <Option value="1280*720">1280×720 (横版)</Option>
                <Option value="720*1280">720×1280 (竖版)</Option>
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Form.Item label="随机种子" name="seed">
              <InputNumber
                min={0}
                max={4294967290}
                style={{ width: '100%' }}
                placeholder="可选"
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
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
