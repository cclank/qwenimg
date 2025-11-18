/**
 * 创作配置对话框 - 紧凑高级设计
 */
import React, { useState } from 'react';
import {
  Form, Input, Select, Upload, message, InputNumber,
  Switch, Dropdown, type MenuProps
} from 'antd';
import {
  PictureOutlined, VideoCameraOutlined,
  UploadOutlined, SettingOutlined,
  ArrowUpOutlined, ThunderboltOutlined
} from '@ant-design/icons';
import { api } from '@/services/api';
import { useAppStore } from '@/store';

const { TextArea } = Input;
const { Option } = Select;

interface CreationDialogProps {
  onSubmit?: () => void;
}

type TaskType = 'text_to_image' | 'text_to_video' | 'image_to_video';
type MediaMode = 'image' | 'video';

export const CreationDialog: React.FC<CreationDialogProps> = ({ onSubmit }) => {
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);

  const [form] = Form.useForm();
  const [mediaMode, setMediaMode] = useState<MediaMode>('image');
  const [taskType, setTaskType] = useState<TaskType>('text_to_image');
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);

  // 处理模式切换
  const handleModeChange = (mode: MediaMode) => {
    setMediaMode(mode);
    if (mode === 'image') {
      setTaskType('text_to_image');
    } else {
      setTaskType(imageUrl ? 'image_to_video' : 'text_to_video');
    }
  };

  // 处理图片上传
  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.uploadImage(formData);
      setImageUrl(res.data.url);
      form.setFieldValue('image_url', res.data.url);

      if (mediaMode === 'video') {
        setTaskType('image_to_video');
      }

      message.success('图片上传成功');
    } catch (error) {
      message.error('图片上传失败');
    }

    return false;
  };

  // 提交创作任务
  const handleSubmit = async (values: any) => {
    if (loading) return;

    try {
      setLoading(true);

      const params = {
        ...values,
        session_id: sessionId,
      };

      let response;
      switch (taskType) {
        case 'text_to_image':
          response = await api.textToImage(params);
          break;
        case 'text_to_video':
          response = await api.textToVideo(params);
          break;
        case 'image_to_video':
          response = await api.imageToVideo(params);
          break;
      }

      // 添加到任务列表
      addTask({
        task_id: response.data.task_id,
        task_type: taskType,
        status: 'pending',
        progress: 0,
        prompt: values.prompt,
        created_at: new Date().toISOString(),
      });

      message.success('任务已提交');
      onSubmit?.();
    } catch (error: any) {
      message.error(error.response?.data?.message || '提交失败');
    } finally {
      setLoading(false);
    }
  };

  // 配置菜单选项
  const modelOptions: MenuProps['items'] = [
    { key: 'wan2.5-t2i-preview', label: 'Wan 2.5 Image' },
    { key: 'wan2.5-t2v-preview', label: 'Wan 2.5 Video' },
  ];

  const aspectRatioOptions: MenuProps['items'] = [
    { key: '1024*1024', label: '1:1' },
    { key: '1280*720', label: '16:9' },
    { key: '720*1280', label: '9:16' },
    { key: '1024*768', label: '4:3' },
  ];

  const numberOptions: MenuProps['items'] = [
    { key: '1', label: '1' },
    { key: '2', label: '2' },
    { key: '3', label: '3' },
    { key: '4', label: '4' },
  ];

  return (
    <div className="creation-dialog">
      <Form
        form={form}
        onFinish={handleSubmit}
        layout="vertical"
        initialValues={{
          model: 'wan2.5-t2i-preview',
          n: 4,
          size: '1024*1024',
          resolution: '1080P',
          duration: 10,
          watermark: false,
        }}
      >
        {/* 对话框头部 */}
        <div className="dialog-header">
          <div className="dialog-tabs-container">
            <div className="dialog-tabs">
              {/* 图片上传按钮 */}
              {mediaMode === 'video' && (
                <Form.Item name="image_upload" noStyle>
                  <Upload
                    accept="image/*"
                    beforeUpload={handleUpload as any}
                    maxCount={1}
                    showUploadList={false}
                  >
                    <button
                      type="button"
                      className="control-select-btn"
                      style={{
                        height: '74px',
                        aspectRatio: '1.72',
                        border: '2px dashed var(--color-border)',
                        borderRadius: 'var(--radius-md)'
                      }}
                    >
                      <PictureOutlined />
                      <span>Image refs</span>
                    </button>
                  </Upload>
                </Form.Item>
              )}
            </div>
          </div>

          {/* 模式切换器 */}
          <div className="dialog-mode-selector">
            <div className="mode-toggle">
              <button
                type="button"
                className={`mode-toggle-btn ${mediaMode === 'image' ? 'active' : ''}`}
                onClick={() => handleModeChange('image')}
              >
                <PictureOutlined />
                <span>Image</span>
              </button>
              <button
                type="button"
                className={`mode-toggle-btn ${mediaMode === 'video' ? 'active' : ''}`}
                onClick={() => handleModeChange('video')}
              >
                <VideoCameraOutlined />
                <span>Video</span>
              </button>
            </div>
          </div>
        </div>

        {/* 输入区域 */}
        <div className="dialog-input-area">
          <div className="dialog-textarea-wrapper">
            <Form.Item name="prompt" noStyle>
              <textarea
                className="dialog-textarea"
                placeholder={
                  mediaMode === 'image'
                    ? 'Describe your image...'
                    : 'Describe your video scene...'
                }
                maxLength={2000}
              />
            </Form.Item>
          </div>
        </div>

        {/* 底部控制栏 */}
        <div className="dialog-footer">
          {/* 左侧控制按钮 - 桌面端显示 */}
          <div className="dialog-controls">
            <Dropdown menu={{ items: modelOptions }} placement="topLeft">
              <button type="button" className="control-select-btn">
                <PictureOutlined />
                <span>{mediaMode === 'image' ? 'Wan 2.5 Image' : 'Wan 2.5 Video'}</span>
              </button>
            </Dropdown>

            {mediaMode === 'image' && (
              <>
                <Form.Item name="size" noStyle>
                  <Select
                    style={{ display: 'none' }}
                    options={[
                      { value: '1024*1024', label: '1:1' },
                      { value: '1280*720', label: '16:9' },
                      { value: '720*1280', label: '9:16' },
                      { value: '1024*768', label: '4:3' },
                    ]}
                  />
                </Form.Item>
                <Dropdown menu={{ items: aspectRatioOptions }} placement="topLeft">
                  <button type="button" className="control-select-btn">
                    <div style={{
                      width: '20px',
                      height: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <div style={{
                        width: '13px',
                        height: '13px',
                        border: '1.5px solid currentColor',
                        borderRadius: '2px'
                      }} />
                    </div>
                    <span>1:1</span>
                  </button>
                </Dropdown>

                <Form.Item name="n" noStyle>
                  <Select style={{ display: 'none' }} />
                </Form.Item>
                <Dropdown menu={{ items: numberOptions }} placement="topLeft">
                  <button type="button" className="control-select-btn">
                    <ThunderboltOutlined />
                    <span>4</span>
                  </button>
                </Dropdown>
              </>
            )}

            {mediaMode === 'video' && (
              <>
                <Form.Item name="resolution" noStyle>
                  <Select style={{ display: 'none' }}>
                    <Option value="480P">480P</Option>
                    <Option value="720P">720P</Option>
                    <Option value="1080P">1080P</Option>
                  </Select>
                </Form.Item>

                <Form.Item name="duration" noStyle>
                  <Select style={{ display: 'none' }}>
                    <Option value={5}>5秒</Option>
                    <Option value={10}>10秒</Option>
                  </Select>
                </Form.Item>
              </>
            )}
          </div>

          {/* 右侧动作按钮 */}
          <div className="dialog-actions">
            <div className="credit-display">
              <ThunderboltOutlined />
              <span>1,661</span>
            </div>
            <button
              type="submit"
              className="generate-btn"
              disabled={loading}
              aria-label="Generate"
            >
              <ArrowUpOutlined />
            </button>
          </div>
        </div>

        {/* 隐藏的表单字段 */}
        <Form.Item name="image_url" hidden>
          <Input />
        </Form.Item>
        <Form.Item name="negative_prompt" hidden>
          <Input />
        </Form.Item>
        <Form.Item name="seed" hidden>
          <InputNumber />
        </Form.Item>
        <Form.Item name="watermark" hidden valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item name="model" hidden>
          <Input />
        </Form.Item>
      </Form>
    </div>
  );
};
