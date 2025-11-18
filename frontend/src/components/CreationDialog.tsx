/**
 * 创作配置对话框 - 紧凑高级设计
 */
import React, { useState } from 'react';
import {
  Form, Input, Select, Upload, message, InputNumber,
  Switch, Dropdown, Modal, type MenuProps
} from 'antd';
import {
  PictureOutlined, VideoCameraOutlined,
  UploadOutlined, SettingOutlined,
  ArrowUpOutlined, NumberOutlined
} from '@ant-design/icons';
import api, { generationAPI } from '@/services/api';
import { useAppStore } from '@/store';

const { TextArea } = Input;
const { Option } = Select;

interface CreationDialogProps {
  onSubmit?: () => void;
}

type TaskType = 'text_to_image' | 'text_to_video' | 'image_to_video';
type MediaMode = 'image' | 'video' | 'image_to_video';

export const CreationDialog: React.FC<CreationDialogProps> = ({ onSubmit }) => {
  const sessionId = useAppStore((state) => state.sessionId);
  const addTask = useAppStore((state) => state.addTask);

  const [form] = Form.useForm();
  const [mediaMode, setMediaMode] = useState<MediaMode>('image');
  const [taskType, setTaskType] = useState<TaskType>('text_to_image');
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 处理模式切换
  const handleModeChange = (mode: MediaMode) => {
    setMediaMode(mode);
    if (mode === 'image') {
      setTaskType('text_to_image');
    } else if (mode === 'video') {
      setTaskType('text_to_video');
    } else if (mode === 'image_to_video') {
      setTaskType('image_to_video');
    }
  };

  // 处理图片上传
  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await generationAPI.uploadImage(formData);
      setImageUrl(res.url);
      form.setFieldValue('image_url', res.url);

      if (mediaMode === 'video' || mediaMode === 'image_to_video') {
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
          response = await generationAPI.textToImage(params);
          break;
        case 'text_to_video':
          response = await generationAPI.textToVideo(params);
          break;
        case 'image_to_video':
          response = await generationAPI.imageToVideo(params);
          break;
      }

      // 添加到任务列表
      addTask({
        task_id: response.task_id,
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
          n: 1,
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
              {(mediaMode === 'video' || mediaMode === 'image_to_video') && (
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

          {/* 右上角模式切换器 */}
          <div className="dialog-mode-selector-top-right">
            <div className="mode-toggle-icons">
              <button
                type="button"
                className={`mode-icon-btn ${mediaMode === 'image' ? 'active' : ''}`}
                onClick={() => {
                  setMediaMode('image');
                  setTaskType('text_to_image');
                }}
                title="文生图"
              >
                <PictureOutlined />
              </button>
              <button
                type="button"
                className={`mode-icon-btn ${mediaMode === 'video' ? 'active' : ''}`}
                onClick={() => {
                  setMediaMode('video');
                  setTaskType('text_to_video');
                }}
                title="文生视频"
              >
                <VideoCameraOutlined />
              </button>
              <button
                type="button"
                className={`mode-icon-btn ${mediaMode === 'image_to_video' ? 'active' : ''}`}
                onClick={() => {
                  setMediaMode('image_to_video');
                  setTaskType('image_to_video');
                }}
                title="图生视频"
              >
                <div className="image-to-video-single-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="1.5"/>
                    <path d="M8 10C8 8.89543 8.89543 8 10 8H14C15.1046 8 16 8.89543 16 10V14C16 15.1046 15.1046 16 14 16H10C8.89543 16 8 15.1046 8 14V10Z" stroke="currentColor" strokeWidth="1.5"/>
                    <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
                    <path d="M16 8L19 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                    <path d="M16 16L19 19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                  </svg>
                </div>
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
                    : mediaMode === 'video'
                    ? 'Describe your video scene...'
                    : imageUrl
                    ? 'Describe how you want to transform this image into a video...'
                    : 'First upload an image, then describe how you want to transform it into a video...'
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
                    <NumberOutlined />
                    <span>{form.getFieldValue('n') || 1}</span>
                  </button>
                </Dropdown>
              </>
            )}

            {(mediaMode === 'video' || mediaMode === 'image_to_video') && (
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

            {/* 高级配置按钮 */}
            <button
              type="button"
              className="control-select-btn"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              <SettingOutlined />
              <span>高级</span>
            </button>
          </div>

          {/* 右侧动作按钮 */}
          <div className="dialog-actions">
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

        {/* 高级配置区域 */}
        {showAdvanced && (
          <div className="advanced-settings">
            <div className="advanced-settings-content">
              <Form.Item
                name="negative_prompt"
                label="负面提示词"
                rules={[{ max: 1000, message: '负面提示词不能超过1000个字符' }]}
              >
                <Input.TextArea
                  placeholder="输入不希望在生成结果中出现的内容..."
                  autoSize={{ minRows: 2, maxRows: 4 }}
                  maxLength={1000}
                />
              </Form.Item>

              <div className="advanced-settings-row">
                <Form.Item
                  name="seed"
                  label="随机种子"
                  rules={[{ pattern: /^\d+$/, message: '请输入数字' }]}
                >
                  <InputNumber
                    placeholder="随机种子"
                    style={{ width: '100%' }}
                    min={0}
                  />
                </Form.Item>

                <Form.Item
                  name="watermark"
                  label="水印"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </div>
            </div>
          </div>
        )}

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
