import { Outlet, useNavigate } from 'react-router-dom'
import { Layout as AntLayout, Menu, Avatar, Dropdown, Badge } from 'antd'
import {
  DashboardOutlined,
  ShoppingOutlined,
  ShoppingCartOutlined,
  ShopOutlined,
  TagsOutlined,
  LogoutOutlined,
  UserOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'
import { useState } from 'react'
import { useAuthStore } from '../store/authStore'

const { Header, Sider, Content } = AntLayout

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/products', icon: <ShoppingOutlined />, label: 'Ürünler' },
    { key: '/orders', icon: <ShoppingCartOutlined />, label: 'Siparişler' },
    { key: '/stores', icon: <ShopOutlined />, label: 'Mağazalar' },
    { key: '/categories', icon: <TagsOutlined />, label: 'Kategoriler' },
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profil',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Çıkış Yap',
      danger: true,
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout()
      navigate('/login')
    }
  }

  return (
    <AntLayout className="min-h-screen">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="light"
        className="border-r border-gray-200"
      >
        <div className="h-16 flex items-center justify-center border-b border-gray-200">
          <h1 className={`text-xl font-bold text-blue-600 ${collapsed ? 'text-sm' : ''}`}>
            {collapsed ? 'PZ' : 'Prapazar'}
          </h1>
        </div>
        <Menu
          mode="inline"
          defaultSelectedKeys={['/']}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          className="border-r-0"
        />
      </Sider>
      <AntLayout>
        <Header className="bg-white border-b border-gray-200 px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="text-gray-500 hover:text-gray-700"
            >
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </button>
          </div>
          <div className="flex items-center gap-4">
            <Badge count={5} size="small">
              <BellOutlined className="text-xl text-gray-500 cursor-pointer" />
            </Badge>
            <Dropdown
              menu={{ items: userMenuItems, onClick: handleMenuClick }}
              placement="bottomRight"
            >
              <div className="flex items-center gap-2 cursor-pointer">
                <Avatar icon={<UserOutlined />} size="small" />
                <span className="text-sm font-medium hidden md:block">
                  {user?.full_name || user?.username}
                </span>
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content className="m-6 p-6 bg-white rounded-lg shadow-sm">
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  )
}
