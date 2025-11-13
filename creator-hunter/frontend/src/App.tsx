import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout, Menu, theme } from 'antd'
import {
  DashboardOutlined,
  TeamOutlined,
  MessageOutlined,
  FileTextOutlined,
  UserOutlined,
  BarChartOutlined,
  SettingOutlined
} from '@ant-design/icons'
import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Targets from './pages/Targets'
import Templates from './pages/Templates'
import Accounts from './pages/Accounts'
import Messages from './pages/Messages'
import Analytics from './pages/Analytics'

const { Header, Content, Sider } = Layout

const menuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: '仪表板'
  },
  {
    key: '/targets',
    icon: <TeamOutlined />,
    label: '目标管理'
  },
  {
    key: '/templates',
    icon: <FileTextOutlined />,
    label: '话术管理'
  },
  {
    key: '/accounts',
    icon: <UserOutlined />,
    label: '账号管理'
  },
  {
    key: '/messages',
    icon: <MessageOutlined />,
    label: '消息记录'
  },
  {
    key: '/analytics',
    icon: <BarChartOutlined />,
    label: '数据分析'
  }
]

function App() {
  const [collapsed, setCollapsed] = useState(false)
  const {
    token: { colorBgContainer },
  } = theme.useToken()

  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
          <div style={{
            height: 32,
            margin: 16,
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold'
          }}>
            {!collapsed ? 'Creator Hunter' : 'CH'}
          </div>
          <Menu
            theme="dark"
            defaultSelectedKeys={['/']}
            mode="inline"
            items={menuItems}
            onClick={({ key }) => {
              window.location.hash = key
            }}
          />
        </Sider>
        <Layout>
          <Header style={{ padding: 0, background: colorBgContainer }}>
            <div style={{
              padding: '0 24px',
              fontSize: 20,
              fontWeight: 'bold'
            }}>
              AIGC达人自动化建联工具
            </div>
          </Header>
          <Content style={{ margin: '16px' }}>
            <div
              style={{
                padding: 24,
                minHeight: 360,
                background: colorBgContainer,
                borderRadius: 8,
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/targets" element={<Targets />} />
                <Route path="/templates" element={<Templates />} />
                <Route path="/accounts" element={<Accounts />} />
                <Route path="/messages" element={<Messages />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </Content>
        </Layout>
      </Layout>
    </BrowserRouter>
  )
}

export default App
