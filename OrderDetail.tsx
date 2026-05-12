import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Table, Button, Modal, Form, Input, Select, Tag,
  message, Popconfirm, Card, Space, Switch, Tooltip
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  CheckCircleOutlined, CloseCircleOutlined, SyncOutlined,
  LinkOutlined, ShopOutlined
} from '@ant-design/icons'
import { storeApi } from '../services/api'

// Platform ikonları ve renkleri
const PLATFORM_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  trendyol: { label: 'Trendyol', color: '#f27a1a', icon: '🔶' },
  hepsiburada: { label: 'Hepsiburada', color: '#ff6000', icon: '🟠' },
  n11: { label: 'N11', color: '#5d3ebc', icon: '🟣' },
  gittigidiyor: { label: 'Gittigidiyor', color: '#368c4c', icon: '🟢' },
  koctas: { label: 'Koçtaş', color: '#003087', icon: '🔵' },
  pazarama: { label: 'Pazarama', color: '#e31837', icon: '🔴' },
  pttavm: { label: 'PTT AVM', color: '#ffd700', icon: '🟡' },
  amazon: { label: 'Amazon', color: '#ff9900', icon: '📦' },
}

export default function Stores() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingStore, setEditingStore] = useState<any>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['stores'],
    queryFn: () => storeApi.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => storeApi.create(data),
    onSuccess: () => {
      message.success('Mağaza eklendi')
      setIsModalOpen(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['stores'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Ekleme başarısız')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => storeApi.update(id, data),
    onSuccess: () => {
      message.success('Mağaza güncellendi')
      setIsModalOpen(false)
      queryClient.invalidateQueries({ queryKey: ['stores'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => storeApi.delete(id),
    onSuccess: () => {
      message.success('Mağaza silindi')
      queryClient.invalidateQueries({ queryKey: ['stores'] })
    },
  })

  const testConnectionMutation = useMutation({
    mutationFn: (id: number) => storeApi.testConnection(id),
    onSuccess: (data) => {
      if (data.data.success) {
        message.success(data.data.message)
      } else {
        message.error(data.data.message)
      }
      queryClient.invalidateQueries({ queryKey: ['stores'] })
    },
  })

  const syncMutation = useMutation({
    mutationFn: (id: number) => storeApi.sync(id),
    onSuccess: () => {
      message.success('Senkronizasyon başlatıldı')
    },
  })

  const platformOptions = Object.entries(PLATFORM_CONFIG).map(([value, config]) => ({
    value,
    label: (
      <span>
        <span style={{ marginRight: 8 }}>{config.icon}</span>
        {config.label}
      </span>
    ),
  }))

  const columns = [
    {
      title: 'Mağaza',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg font-bold"
            style={{ backgroundColor: PLATFORM_CONFIG[record.platform]?.color || '#999' }}
          >
            {PLATFORM_CONFIG[record.platform]?.icon || '🏪'}
          </div>
          <div>
            <p className="font-medium">{text}</p>
            <p className="text-xs text-gray-500">{record.store_name}</p>
          </div>
        </div>
      ),
    },
    {
      title: 'Platform',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform: string) => (
        <Tag
          color={PLATFORM_CONFIG[platform]?.color}
          style={{ color: '#fff', fontWeight: 'bold' }}
        >
          {PLATFORM_CONFIG[platform]?.icon} {PLATFORM_CONFIG[platform]?.label || platform}
        </Tag>
      ),
    },
    {
      title: 'Satıcı ID',
      dataIndex: 'seller_id',
      key: 'seller_id',
    },
    {
      title: 'Durum',
      key: 'status',
      render: (_: any, record: any) => (
        <Space>
          <Tooltip title={record.is_active ? 'Aktif' : 'Pasif'}>
            <Tag color={record.is_active ? 'success' : 'error'}>
              {record.is_active ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            </Tag>
          </Tooltip>
          <Tooltip title={record.is_connected ? 'Bağlı' : 'Bağlı Değil'}>
            <Tag color={record.is_connected ? 'success' : 'warning'}>
              {record.is_connected ? '🔗' : '❌'}
            </Tag>
          </Tooltip>
        </Space>
      ),
    },
    {
      title: 'Son Senkronizasyon',
      dataIndex: 'last_sync_at',
      key: 'last_sync_at',
      render: (date: string) => date ? new Date(date).toLocaleString('tr-TR') : 'Henüz yapılmadı',
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 320,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            icon={<LinkOutlined />}
            size="small"
            onClick={() => testConnectionMutation.mutate(record.id)}
            loading={testConnectionMutation.isPending}
          >
            Test
          </Button>
          <Button
            icon={<SyncOutlined />}
            size="small"
            type="primary"
            ghost
            onClick={() => syncMutation.mutate(record.id)}
            loading={syncMutation.isPending}
            disabled={!record.is_connected}
          >
            Senkronize
          </Button>
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => {
              setEditingStore(record)
              form.setFieldsValue(record)
              setIsModalOpen(true)
            }}
          />
          <Popconfirm
            title="Mağazayı sil"
            description="Bu mağazayı silmek istediğinize emin misiniz?"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="Evet"
            cancelText="Hayır"
          >
            <Button icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Mağazalar</h1>
          <p className="text-gray-500 text-sm mt-1">
            Trendyol, Hepsiburada, N11, Koçtaş, Pazarama, PTT AVM ve daha fazlası
          </p>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={() => {
            setEditingStore(null)
            form.resetFields()
            setIsModalOpen(true)
          }}
        >
          Yeni Mağaza
        </Button>
      </div>

      {/* Platform Özeti Kartları */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
        {Object.entries(PLATFORM_CONFIG).map(([key, config]) => {
          const count = data?.filter((s: any) => s.platform === key).length || 0
          return (
            <Card
              key={key}
              className="text-center cursor-pointer hover:shadow-md transition-shadow"
              bodyStyle={{ padding: '12px' }}
            >
              <div className="text-2xl mb-1">{config.icon}</div>
              <div className="text-xs font-medium text-gray-600">{config.label}</div>
              <div className="text-lg font-bold" style={{ color: config.color }}>
                {count}
              </div>
            </Card>
          )
        })}
      </div>

      <Table
        dataSource={data || []}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={
          <div className="flex items-center gap-2">
            <ShopOutlined />
            {editingStore ? 'Mağaza Düzenle' : 'Yeni Mağaza Ekle'}
          </div>
        }
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => {
            if (editingStore) {
              updateMutation.mutate({ id: editingStore.id, data: values })
            } else {
              createMutation.mutate(values)
            }
          }}
        >
          <Form.Item
            name="name"
            label="Mağaza Adı"
            rules={[{ required: true, message: 'Mağaza adı girin' }]}
          >
            <Input placeholder="Örn: Trendyol Ana Mağaza" size="large" />
          </Form.Item>

          <Form.Item
            name="platform"
            label="Pazaryeri Platformu"
            rules={[{ required: true, message: 'Platform seçin' }]}
          >
            <Select
              options={platformOptions}
              placeholder="Platform seçin"
              size="large"
              disabled={!!editingStore}
            />
          </Form.Item>

          <Form.Item
            name="store_name"
            label="Pazaryeri Mağaza Adı"
          >
            <Input placeholder="Pazaryerindeki mağaza adı" />
          </Form.Item>

          <Form.Item
            name="seller_id"
            label="Satıcı ID / Mağaza Kodu"
            rules={[{ required: true }]}
          >
            <Input placeholder="Satıcı ID veya Mağaza Kodu" />
          </Form.Item>

          <Form.Item
            name="api_key"
            label="API Key / Client ID / Kullanıcı Adı"
            rules={[{ required: true }]}
          >
            <Input.Password placeholder="API Key, Client ID veya Kullanıcı Adı" />
          </Form.Item>

          <Form.Item
            name="api_secret"
            label="API Secret / Client Secret / Şifre"
            rules={[{ required: true }]}
          >
            <Input.Password placeholder="API Secret, Client Secret veya Şifre" />
          </Form.Item>

          <Form.Item
            name="base_url"
            label="Özel API URL (Opsiyonel)"
          >
            <Input placeholder="Varsayılan URL kullanılacak" />
          </Form.Item>

          <div className="grid grid-cols-2 gap-4">
            <Form.Item
              name="commission_rate"
              label="Komisyon Oranı (%)"
            >
              <Input type="number" placeholder="0" min={0} max={100} />
            </Form.Item>

            <Form.Item
              name="sync_interval_minutes"
              label="Senkronizasyon Aralığı (dk)"
            >
              <Input type="number" placeholder="15" min={5} max={1440} />
            </Form.Item>
          </div>

          <Button
            type="primary"
            htmlType="submit"
            block
            size="large"
            loading={createMutation.isPending || updateMutation.isPending}
          >
            {editingStore ? 'Güncelle' : 'Oluştur'}
          </Button>
        </Form>
      </Modal>
    </div>
  )
}
