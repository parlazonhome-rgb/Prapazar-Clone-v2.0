import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card, Descriptions, Tag, Button, Form, Input, InputNumber,
  Upload, message, Tabs, Table, Space, Switch, Row, Col
} from 'antd'
import {
  ArrowLeftOutlined, SaveOutlined, UploadOutlined,
  PlusOutlined, DeleteOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { productApi, storeApi } from '../services/api'

const { TabPane } = Tabs
const { TextArea } = Input

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const productId = parseInt(id || '0')
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form] = Form.useForm()
  const [isEditing, setIsEditing] = useState(false)

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => productApi.get(productId).then((r) => r.data),
  })

  const { data: stores } = useQuery({
    queryKey: ['stores'],
    queryFn: () => storeApi.list().then((r) => r.data),
  })

  const updateMutation = useMutation({
    mutationFn: (data: any) => productApi.update(productId, data),
    onSuccess: () => {
      message.success('Ürün güncellendi')
      queryClient.invalidateQueries({ queryKey: ['product', productId] })
      setIsEditing(false)
    },
  })

  const syncMutation = useMutation({
    mutationFn: ({ productId, storeId }: { productId: number; storeId: number }) =>
      productApi.sync(productId, storeId),
    onSuccess: () => message.success('Senkronizasyon başlatıldı'),
  })

  if (isLoading) {
    return <div className="text-center py-10">Yükleniyor...</div>
  }

  if (!product) {
    return <div className="text-center py-10">Ürün bulunamadı</div>
  }

  const variantColumns = [
    { title: 'SKU', dataIndex: 'sku', key: 'sku' },
    { title: 'Barkod', dataIndex: 'barcode', key: 'barcode' },
    { title: 'Özellikler', dataIndex: 'attributes', key: 'attributes',
      render: (attrs: any) => Object.entries(attrs || {}).map(([k, v]) => `${k}: ${v}`).join(', ')
    },
    { title: 'Fiyat', dataIndex: 'price', key: 'price', render: (v: number) => `₺${v?.toFixed(2)}` },
    { title: 'Stok', dataIndex: 'stock_quantity', key: 'stock' },
    { title: 'Durum', dataIndex: 'is_active', key: 'status',
      render: (active: boolean) => <Tag color={active ? 'green' : 'red'}>{active ? 'Aktif' : 'Pasif'}</Tag>
    },
  ]

  const platformColumns = [
    { title: 'Mağaza', dataIndex: ['store', 'name'], key: 'store' },
    { title: 'Platform ID', dataIndex: 'platform_product_id', key: 'platform_id' },
    { title: 'Platform Fiyat', dataIndex: 'platform_price', key: 'price', render: (v: number) => `₺${v?.toFixed(2)}` },
    { title: 'Platform Stok', dataIndex: 'platform_stock', key: 'stock' },
    { title: 'Durum', dataIndex: 'status', key: 'status',
      render: (status: string) => <Tag color={status === 'active' ? 'green' : 'orange'}>{status}</Tag>
    },
    { title: 'Senkronizasyon', dataIndex: 'sync_status', key: 'sync',
      render: (status: string) => <Tag color={status === 'synced' ? 'green' : status === 'failed' ? 'red' : 'orange'}>{status}</Tag>
    },
    {
      title: 'İşlem',
      key: 'action',
      render: (_: any, record: any) => (
        <Button
          size="small"
          onClick={() => syncMutation.mutate({ productId, storeId: record.store_id })}
          loading={syncMutation.isPending}
        >
          Senkronize
        </Button>
      ),
    },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/products')}>
            Geri
          </Button>
          <h1 className="text-2xl font-bold">{product.title}</h1>
        </div>
        <Button
          type={isEditing ? 'default' : 'primary'}
          icon={<SaveOutlined />}
          onClick={() => {
            if (isEditing) {
              form.submit()
            } else {
              setIsEditing(true)
              form.setFieldsValue(product)
            }
          }}
        >
          {isEditing ? 'Kaydet' : 'Düzenle'}
        </Button>
      </div>

      <Tabs defaultActiveKey="1">
        <TabPane tab="Genel Bilgiler" key="1">
          {isEditing ? (
            <Form
              form={form}
              layout="vertical"
              onFinish={(values) => updateMutation.mutate(values)}
            >
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="sku" label="SKU" rules={[{ required: true }]}>
                    <Input />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="barcode" label="Barkod">
                    <Input />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item name="title" label="Ürün Adı" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="description" label="Açıklama">
                <TextArea rows={4} />
              </Form.Item>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="base_price" label="Satış Fiyatı">
                    <InputNumber style={{ width: '100%' }} prefix="₺" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="purchase_price" label="Alış Fiyatı">
                    <InputNumber style={{ width: '100%' }} prefix="₺" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="stock_quantity" label="Stok">
                    <InputNumber style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item name="brand" label="Marka">
                <Input />
              </Form.Item>
              <Form.Item name="is_active" valuePropName="checked">
                <Switch checkedChildren="Aktif" unCheckedChildren="Pasif" />
              </Form.Item>
            </Form>
          ) : (
            <Descriptions bordered column={2}>
              <Descriptions.Item label="SKU">{product.sku}</Descriptions.Item>
              <Descriptions.Item label="Barkod">{product.barcode || '-'}</Descriptions.Item>
              <Descriptions.Item label="Fiyat" span={2}>
                <span className="text-lg font-bold text-green-600">₺{product.base_price?.toFixed(2)}</span>
              </Descriptions.Item>
              <Descriptions.Item label="Stok">
                <Tag color={product.stock_quantity <= product.stock_alert_level ? 'red' : 'green'}>
                  {product.stock_quantity} adet
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Marka">{product.brand || '-'}</Descriptions.Item>
              <Descriptions.Item label="Durum" span={2}>
                <Tag color={product.is_active ? 'green' : 'red'}>
                  {product.is_active ? 'Aktif' : 'Pasif'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Açıklama" span={2}>
                {product.description || '-'}
              </Descriptions.Item>
            </Descriptions>
          )}
        </TabPane>

        <TabPane tab="Varyantlar" key="2">
          <Table
            dataSource={product.variants || []}
            columns={variantColumns}
            rowKey="id"
            pagination={false}
          />
        </TabPane>

        <TabPane tab="Pazaryerleri" key="3">
          <Table
            dataSource={product.platforms || []}
            columns={platformColumns}
            rowKey="id"
          />
        </TabPane>

        <TabPane tab="Görseller" key="4">
          <div className="grid grid-cols-4 gap-4">
            {product.images?.map((url: string, index: number) => (
              <div key={index} className="relative group">
                <img src={url} alt="" className="w-full h-40 object-cover rounded-lg" />
              </div>
            ))}
            <div className="border-2 border-dashed border-gray-300 rounded-lg h-40 flex items-center justify-center cursor-pointer hover:border-blue-500">
              <Upload showUploadList={false}>
                <div className="text-center">
                  <UploadOutlined className="text-2xl text-gray-400" />
                  <p className="text-gray-400 mt-2">Görsel Ekle</p>
                </div>
              </Upload>
            </div>
          </div>
        </TabPane>
      </Tabs>
    </div>
  )
}
