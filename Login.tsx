import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Table, Button, Input, Space, Tag, Modal, Form,
  message, Popconfirm, Upload, Card, Select, Row, Col
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  SyncOutlined, ImportOutlined, SearchOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { productApi, storeApi } from '../services/api'

const { Search } = Input

export default function Products() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<any>(null)
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['products', page, pageSize, search],
    queryFn: () =>
      productApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
      }).then((r) => r.data),
  })

  const { data: stores } = useQuery({
    queryKey: ['stores'],
    queryFn: () => storeApi.list().then((r) => r.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => productApi.delete(id),
    onSuccess: () => {
      message.success('Ürün silindi')
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Silme başarısız')
    },
  })

  const syncMutation = useMutation({
    mutationFn: ({ productId, storeId }: { productId: number; storeId: number }) =>
      productApi.sync(productId, storeId),
    onSuccess: () => {
      message.success('Senkronizasyon başlatıldı')
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Senkronizasyon başarısız')
    },
  })

  const importMutation = useMutation({
    mutationFn: (file: File) => productApi.importExcel(file),
    onSuccess: (data) => {
      message.success(`İçe aktarma tamamlandı: ${data.data.imported} yeni, ${data.data.updated} güncellendi`)
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'İçe aktarma başarısız')
    },
  })

  const columns = [
    {
      title: 'Görsel',
      dataIndex: 'main_image',
      key: 'image',
      width: 80,
      render: (url: string) =>
        url ? (
          <img src={url} alt="" className="w-12 h-12 object-cover rounded" />
        ) : (
          <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center text-gray-400 text-xs">
            Yok
          </div>
        ),
    },
    {
      title: 'Ürün',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: any) => (
        <div>
          <p className="font-medium">{text}</p>
          <p className="text-xs text-gray-500">SKU: {record.sku}</p>
        </div>
      ),
    },
    {
      title: 'Fiyat',
      dataIndex: 'base_price',
      key: 'price',
      render: (price: number) => `₺${price?.toFixed(2)}`,
    },
    {
      title: 'Stok',
      dataIndex: 'stock_quantity',
      key: 'stock',
      render: (stock: number, record: any) => (
        <Tag color={stock <= record.stock_alert_level ? 'red' : stock <= 10 ? 'orange' : 'green'}>
          {stock} adet
        </Tag>
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
      title: 'Pazaryerleri',
      dataIndex: 'platforms',
      key: 'platforms',
      render: (platforms: any[]) => (
        <Space size="small">
          {platforms?.map((p: any) => (
            <Tag
              key={p.id}
              color={p.sync_status === 'synced' ? 'green' : p.sync_status === 'failed' ? 'red' : 'orange'}
              size="small"
            >
              {p.store?.platform}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 200,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => navigate(`/products/${record.id}`)}
          />
          <Popconfirm
            title="Ürünü sil"
            description="Bu ürünü silmek istediğinize emin misiniz?"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="Evet"
            cancelText="Hayır"
          >
            <Button icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
          {stores?.map((store: any) => (
            <Button
              key={store.id}
              icon={<SyncOutlined />}
              size="small"
              onClick={() => syncMutation.mutate({ productId: record.id, storeId: store.id })}
              loading={syncMutation.isPending}
            >
              {store.platform}
            </Button>
          ))}
        </Space>
      ),
    },
  ]

  const handleImport = (info: any) => {
    if (info.file.status === 'done') {
      importMutation.mutate(info.file.originFileObj)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Ürünler</h1>
        <Space>
          <Upload
            accept=".xlsx,.xls,.csv"
            showUploadList={false}
            customRequest={({ file }) => importMutation.mutate(file as File)}
          >
            <Button icon={<ImportOutlined />} loading={importMutation.isPending}>
              Excel İçe Aktar
            </Button>
          </Upload>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingProduct(null)
              form.resetFields()
              setIsModalOpen(true)
            }}
          >
            Yeni Ürün
          </Button>
        </Space>
      </div>

      <Card className="mb-4">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12} lg={8}>
            <Search
              placeholder="Ürün ara..."
              allowClear
              enterButton={<SearchOutlined />}
              onSearch={(value) => {
                setSearch(value)
                setPage(1)
              }}
            />
          </Col>
        </Row>
      </Card>

      <Table
        dataSource={data?.items || []}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: data?.total || 0,
          onChange: (p, ps) => {
            setPage(p)
            setPageSize(ps)
          },
          showSizeChanger: true,
          showTotal: (total) => `Toplam ${total} ürün`,
        }}
      />

      <Modal
        title={editingProduct ? 'Ürün Düzenle' : 'Yeni Ürün'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={800}
      >
        <Form form={form} layout="vertical" onFinish={(values) => {
          console.log(values)
          setIsModalOpen(false)
        }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="sku" label="SKU" rules={[{ required: true }]}>
                <Input placeholder="Stok kodu" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="barcode" label="Barkod">
                <Input placeholder="Barkod" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="title" label="Ürün Adı" rules={[{ required: true }]}>
            <Input placeholder="Ürün adı" />
          </Form.Item>
          <Form.Item name="description" label="Açıklama">
            <Input.TextArea rows={3} placeholder="Ürün açıklaması" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="base_price" label="Satış Fiyatı" rules={[{ required: true }]}>
                <Input type="number" placeholder="0.00" prefix="₺" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="purchase_price" label="Alış Fiyatı">
                <Input type="number" placeholder="0.00" prefix="₺" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="stock_quantity" label="Stok Miktarı" rules={[{ required: true }]}>
                <Input type="number" placeholder="0" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large">
              {editingProduct ? 'Güncelle' : 'Oluştur'}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
