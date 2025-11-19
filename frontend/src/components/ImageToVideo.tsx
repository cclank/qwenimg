/**
 * 图生视频组件
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
  Upload,
  message,
} from 'antd';
import {
  ThunderboltOutlined,
  VideoCameraOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import { generationAPI } from '@/services/api';
import { useAppStore } from '@/store';
import type { ImageToVideoRequest } from '@/types';

const { TextArea } = Input;
const { Option } = Select;

export const ImageToVideo: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState<string>('');
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);

  const handleUpload = (file: File) => {
    // 转换为Base64
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result as string;
      setImageUrl(base64);
      form.setFieldValue('image_url', base64);
    };
    reader.readAsDataURL(file);
    return false; // 阻止自动上传
  };

  const handleSubmit = async (values: any) => {
    if (!imageUrl) {
      message.error('请先上传图片');
      return;
    }

    try {
      setLoading(true);
      console.log('Submitting image to video task with session_id:', sessionId);

      const request: ImageToVideoRequest = {
        ...values,
        image_url: imageUrl,
        session_id: sessionId,
      };

      const response = await generationAPI.imageToVideo(request);
      console.log('Task created successfully:', response);

      addTask({
        task_id: response.task_id,
        task_type: 'image_to_video',
        status: 'pending',
        progress: 0,
        prompt: values.prompt || '图生视频',
      });

      message.success('任务已创建，正在生成中...');
    } catch (error: any) {
      console.error('Failed to create task:', error);
      message.error(error.response?.data?.detail || '创建任务失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title={
        <Space>
          <VideoCameraOutlined />
          <span>图生视频</span>
        </Space>
      }
      bordered={false}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          model: 'wan2.5-i2v-preview',
          resolution: '1080P',
          duration: 10,
          watermark: false,
        }}
      >
        <Row gutter={16}>
          <Col xs={24} lg={12}>
            <Form.Item
              label="上传图片"
              name="image_upload"
              rules={[{ required: !imageUrl, message: '请上传图片' }]}
            >
              <Upload.Dragger
                accept="image/*"
                beforeUpload={handleUpload}
                maxCount={1}
                showUploadList={false}
                style={{
                  background: '#fafafa',
                  border: '2px dashed #d9d9d9',
                  borderRadius: '8px',
                  padding: '20px',
                }}
              >
                {imageUrl ? (
                  <div style={{ position: 'relative', width: '100%', height: '200px' }}>
                    <img
                      src={imageUrl}
                      alt="Uploaded"
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'contain',
                        borderRadius: '4px',
                      }}
                    />
                    <div
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        background: 'rgba(0,0,0,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        opacity: 0,
                        transition: 'opacity 0.3s',
                        borderRadius: '4px',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
                      onMouseLeave={(e) => (e.currentTarget.style.opacity = '0')}
                    >
                      点击或拖拽替换图片
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: '20px 0' }}>
                    <p className="ant-upload-drag-icon">
                      <UploadOutlined style={{ fontSize: '32px', color: '#000000' }} />
                    </p>
                    <p className="ant-upload-text" style={{ fontSize: '16px', color: '#333' }}>
                      点击或拖拽图片到此处
                    </p>
                    <p className="ant-upload-hint" style={{ color: '#999' }}>
                      支持 JPG, PNG 等常见格式
                    </p>
                  </div>
                )}
              </Upload.Dragger>
            </Form.Item>
            <Form.Item name="image_url" hidden>
              <Input />
            </Form.Item>
          </Col>

          <Col xs={24} lg={12}>
            <Form.Item label="动作描述（可选）" name="prompt">
              <TextArea
                rows={4}
                placeholder="描述视频中的动作，例如：摄像机缓慢推进，阳光从左侧照射"
                showCount
                maxLength={500}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} lg={12}>
            <Form.Item label="负面提示词" name="negative_prompt">
              <TextArea
                rows={3}
                placeholder="描述你不想要的元素"
                showCount
                maxLength={500}
              />
            </Form.Item>
          </Col>

          <Col xs={24} lg={12}>
            <Row gutter={16}>
              <Col xs={24} sm={12}>
                <Form.Item label="分辨率" name="resolution">
                  <Select>
                    <Option value="480P">480P</Option>
                    <Option value="720P">720P</Option>
                    <Option value="1080P">1080P</Option>
                  </Select>
                </Form.Item>
              </Col>

              <Col xs={24} sm={12}>
                <Form.Item label="时长" name="duration">
                  <Select>
                    <Option value={5}>5秒</Option>
                    <Option value={10}>10秒</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

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
