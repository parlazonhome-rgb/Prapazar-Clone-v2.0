import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Table, Button, Modal, Form, Input, Tag,
  message, Popconfirm, Space, Tabs
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  TagOutlined, LinkOutlined
} from '@ant-design/icons'
import { categoryApi } from '../services/api'

const { TabPane } = Tabs

// Platform konfigürasyonu
const PLATFORMS = [
  { key: 'trendyol', label: 'Trendyol', color: '#f27a1a' },
  { key: 'hepsiburada', label: 'Hepsiburada', color: '#ff6000' },
  { key: 'n11', label: 'N11', color: '#5d3ebc' },
  { key: 'koctas', label: 'Koçtaş', color: '#003087' },
  { key: 'pazarama', label: 'Pazarama', color: '#e31837' },
  { key: 'pttavm', label: 'PTT AVM', color: '#ffd700' },
]

export default function Categories() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState<any>(null)
  const [activeTab, setActiveTab] = useState('general')
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryApi.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => categoryApi.create(data),
    onSuccess: () => {
      message.success('Kategori eklendi')
      setIsModalOpen(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => categoryApi.update(id, data),
    onSuccess: () => {
      message.success('Kategori güncellendi')
      setIsModalOpen(false)
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => categoryApi.delete(id),
    onSuccess: () => {
      message.success('Kategori silindi')
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })

  const columns = [
    {
      title: 'Kategori',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <div>
          <p className="font-medium">{text}</p>
          <p className="text-xs text-gray-500">{record.description}</p>
        </div>
      ),
    },
    {
      title: 'Pazaryeri Eşleştirmeleri',
      key: 'platform_ids',
      width: 400,
      render: (_: any, record: any) => (
        <div className="flex flex-wrap gap-1">
          {PLATFORMS.map((platform) => {
            const id = record[`${platform.key}_category_id`]
            return id ? (
              <Tag
                key={platform.key}
                color={platform.color}
                style={{ color: '#fff', fontSize: '11px' }}
              >
                {platform.label}: {id}
              </Tag>
            ) : null
          })}
        </div>
      ),
    },
    {
      title: 'Durum',
      dataIndex: 'is_active',
      key: 'status',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? 'Aktif' : 'Pasif'}
        </Tag>
      ),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 120,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => {
              setEditingCategory(record)
              form.setFieldsValue(record)
              setIsModalOpen(true)
            }}
          />
          <Popconfirm
            title="Kategoriyi sil"
            onConfirm={() => deleteMutation.mutate(record.id)}
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
          <h1 className="text-2xl font-bold">Kategoriler</h1>
          <p className="text-gray-500 text-sm mt-1">
            Her pazaryeri için kategori eşleştirmelerini yönetin
          </p>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={() => {
            setEditingCategory(null)
            form.resetFields()
            setIsModalOpen(true)
          }}
        >
          Yeni Kategori
        </Button>
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
            <TagOutlined />
            {editingCategory ? 'Kategori Düzenle' : 'Yeni Kategori'}
          </div>
        }
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={700}
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="Genel Bilgiler" key="general">
            <Form
              form={form}
              layout="vertical"
              onFinish={(values) => {
                if (editingCategory) {
                  updateMutation.mutate({ id: editingCategory.id, data: values })
                } else {
                  createMutation.mutate(values)
                }
              }}
            >
              <Form.Item
                name="name"
                label="Kategori Adı"
                rules={[{ required: true }]}
              >
                <Input placeholder="Kategori adı" size="large" />
              </Form.Item>

              <Form.Item name="description" label="Açıklama">
                <Input.TextArea rows={2} placeholder="Açıklama" />
              </Form.Item>

              <Form.Item name="parent_id" label="Üst Kategori">
                <Input type="number" placeholder="Üst kategori ID (opsiyonel)" />
              </Form.Item>

              <Button
                type="primary"
                htmlType="submit"
                block
                size="large"
                loading={createMutation.isPending || updateMutation.isPending}
              >
                {editingCategory ? 'Güncelle' : 'Oluştur'}
              </Button>
            </Form>
          </TabPane>

          <TabPane
            tab={
              <span>
                <LinkOutlined /> Pazaryeri Eşleştirmeleri
              </span>
            }
            key="platforms"
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={(values) => {
                if (editingCategory) {
                  updateMutation.mutate({ id: editingCategory.id, data: values })
                } else {
                  createMutation.mutate(values)
                }
              }}
            >
              <div className="space-y-4">
                {PLATFORMS.map((platform) => (
                  <Form.Item
                    key={platform.key}
                    name={`${platform.key}_category_id`}
                    label={
                      <span className="flex items-center gap-2">
                        <Tag color={platform.color} style={{ color: '#fff' }}>
                          {platform.label}
                        </Tag>
                      </span>
                    }
                  >
                    <Input placeholder={`${platform.label} kategori ID`} />
                  </Form.Item>
                ))}
              </div>

              <Button
                type="primary"
                htmlType="submit"
                block
                size="large"
                loading={createMutation.isPending || updateMutation.isPending}
              >
                {editingCategory ? 'Güncelle' : 'Oluştur'}
              </Button>
            </Form>
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  )
}
