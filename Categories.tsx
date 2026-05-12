import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Table, Button, Input, Space, Tag, Modal, Form,
  message, Select, DatePicker, Card, Row, Col
} from 'antd'
import {
  EyeOutlined, TruckOutlined, CloseCircleOutlined,
  SearchOutlined, FilterOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { orderApi } from '../services/api'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
const { Search } = Input

export default function Orders() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)
  const [isShipmentModalOpen, setIsShipmentModalOpen] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<any>(null)
  const [shipmentForm] = Form.useForm()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['orders', page, pageSize, status, dateRange, search],
    queryFn: () =>
      orderApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        status: status || undefined,
        date_from: dateRange?.[0]?.toISOString(),
        date_to: dateRange?.[1]?.toISOString(),
      }).then((r) => r.data),
  })

  const shipmentMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      orderApi.shipment(id, data),
    onSuccess: () => {
      message.success('Kargo bilgisi güncellendi')
      setIsShipmentModalOpen(false)
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'İşlem başarısız')
    },
  })

  const cancelMutation = useMutation({
    mutationFn: (id: number) => orderApi.cancel(id),
    onSuccess: () => {
      message.success('Sipariş iptal edildi')
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'İptal başarısız')
    },
  })

  const statusOptions = [
    { value: 'new', label: 'Yeni' },
    { value: 'confirmed', label: 'Onaylandı' },
    { value: 'preparing', label: 'Hazırlanıyor' },
    { value: 'shipped', label: 'Kargoda' },
    { value: 'delivered', label: 'Teslim Edildi' },
    { value: 'cancelled', label: 'İptal' },
  ]

  const statusColors: Record<string, string> = {
    new: 'blue',
    confirmed: 'cyan',
    preparing: 'orange',
    shipped: 'purple',
    delivered: 'green',
    cancelled: 'red',
  }

  const statusLabels: Record<string, string> = {
    new: 'Yeni',
    confirmed: 'Onaylandı',
    preparing: 'Hazırlanıyor',
    shipped: 'Kargoda',
    delivered: 'Teslim Edildi',
    cancelled: 'İptal',
  }

  const columns = [
    {
      title: 'Sipariş No',
      dataIndex: 'order_number',
      key: 'order_number',
      render: (text: string, record: any) => (
        <div>
          <p className="font-medium">{text}</p>
          <p className="text-xs text-gray-500">{record.platform_order_number}</p>
        </div>
      ),
    },
    {
      title: 'Müşteri',
      dataIndex: 'customer_name',
      key: 'customer',
      render: (name: string, record: any) => (
        <div>
          <p>{name || 'Bilinmiyor'}</p>
          <p className="text-xs text-gray-500">{record.customer_phone}</p>
        </div>
      ),
    },
    {
      title: 'Mağaza',
      dataIndex: ['store', 'name'],
      key: 'store',
    },
    {
      title: 'Toplam',
      dataIndex: 'total',
      key: 'total',
      render: (total: number) => `₺${total?.toFixed(2)}`,
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={statusColors[status] || 'default'}>
          {statusLabels[status] || status}
        </Tag>
      ),
    },
    {
      title: 'Tarih',
      dataIndex: 'created_at',
      key: 'date',
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 200,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            icon={<EyeOutlined />}
            size="small"
            onClick={() => navigate(`/orders/${record.id}`)}
          >
            Detay
          </Button>
          {record.status === 'preparing' && (
            <Button
              icon={<TruckOutlined />}
              size="small"
              type="primary"
              onClick={() => {
                setSelectedOrder(record)
                shipmentForm.resetFields()
                setIsShipmentModalOpen(true)
              }}
            >
              Kargo
            </Button>
          )}
          {['new', 'confirmed', 'preparing'].includes(record.status) && (
            <Button
              icon={<CloseCircleOutlined />}
              size="small"
              danger
              onClick={() => cancelMutation.mutate(record.id)}
              loading={cancelMutation.isPending}
            >
              İptal
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Siparişler</h1>
      </div>

      <Card className="mb-4">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Search
              placeholder="Sipariş ara..."
              allowClear
              onSearch={(value) => {
                setSearch(value)
                setPage(1)
              }}
            />
          </Col>
          <Col xs={24} md={8}>
            <Select
              placeholder="Durum filtresi"
              allowClear
              style={{ width: '100%' }}
              options={statusOptions}
              onChange={(value) => {
                setStatus(value)
                setPage(1)
              }}
            />
          </Col>
          <Col xs={24} md={8}>
            <RangePicker
              style={{ width: '100%' }}
              onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs] | null)}
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
          showTotal: (total) => `Toplam ${total} sipariş`,
        }}
      />

      <Modal
        title="Kargo Bilgisi"
        open={isShipmentModalOpen}
        onCancel={() => setIsShipmentModalOpen(false)}
        footer={null}
      >
        <Form
          form={shipmentForm}
          layout="vertical"
          onFinish={(values) => {
            if (selectedOrder) {
              shipmentMutation.mutate({
                id: selectedOrder.id,
                data: values,
              })
            }
          }}
        >
          <Form.Item
            name="cargo_company"
            label="Kargo Firması"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { value: 'aras', label: 'Aras Kargo' },
                { value: 'yurtici', label: 'Yurtiçi Kargo' },
                { value: 'mng', label: 'MNG Kargo' },
                { value: 'ptt', label: 'PTT Kargo' },
                { value: 'surat', label: 'Sürat Kargo' },
                { value: 'horoz', label: 'Horoz Lojistik' },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="tracking_number"
            label="Takip Numarası"
            rules={[{ required: true }]}
          >
            <Input placeholder="Kargo takip numarası" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={shipmentMutation.isPending}>
            Kargoya Ver
          </Button>
        </Form>
      </Modal>
    </div>
  )
}
