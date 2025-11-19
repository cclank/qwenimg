import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import App from './App.tsx'
import './index.css'

// 配置dayjs为中文
dayjs.locale('zh-cn')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#000000',
          borderRadius: 6,
          wireframe: false,
          colorBgContainer: '#ffffff',
        },
        components: {
          Button: {
            colorPrimary: '#000000',
            algorithm: true, // Enable algorithm for hover states
          },
          Input: {
            activeBorderColor: '#000000',
            hoverBorderColor: '#000000',
          }
        }
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>,
)
