import { useQuery } from '@tanstack/react-query'
import { Row, Col, Card, Statistic, Table, Tag, Spin } from 'antd'
import {
  ShoppingCartOutlined,
  DollarOutlined,
  PackageOutlined,
  RiseOutlined,
} from '@ant-design/icons'
import { orderApi, productApi } from '../services/api'

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['orderStats'],
    queryFn: () => orderApi.stats().then((r) => r.data),
  })

  const { data: todayOrders, isLoading: ordersLoading } = useQuery({
    queryKey: ['todayOrders'],
    queryFn: () => orderApi.today().then((r) => r.data),
  })

  const { data: lowStock, isLoading: stockLoading } = useQuery({
    queryKey: ['lowStock'],
    queryFn: () => productApi.list({ search: '', limit: 5 }).then((r) => r.data?.items?.filter((p: any) => p.stock_quantity <= p.stock_alert_level) || []),
  })

  const statCards = [
    {
      title: 'Toplam Sipariş',
      value: stats?.total_orders || 0,
      icon: <ShoppingCartOutlined className="text-2xl text-blue-500" />,
      color: 'bg-blue-50',
    },
    {
      title: 'Bugünkü Sipariş',
      value: stats?.today_orders || 0,
      icon: <RiseOutlined className="text-2xl text-green-500" />,
      color: 'bg-green-50',
    },
    {
      title: 'Bekleyen Sipariş',
      value: stats?.pending_orders || 0,
      icon: <PackageOutlined className="text-2xl text-orange-500" />,
      color: 'bg-orange-50',
    },
    {
      title: 'Toplam Ciro',
      value: stats?.total_revenue || 0,
      icon: <DollarOutlined className="text-2xl text-purple-500" />,
      color: 'bg-purple-50',
      prefix: '₺',
    },
  ]

  const orderColumns = [
    { title: 'Sipariş No', dataIndex: 'order_number', key: 'order_number' },
    { title: 'Müşteri', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Toplam', dataIndex: 'total', key: 'total', render: (v: number) => `₺${v?.toFixed(2)}` },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: Record<string, string> = {
          new: 'blue',
          confirmed: 'cyan',
          preparing: 'orange',
          shipped: 'purple',
          delivered: 'green',
          cancelled: 'red',
        }
        const labels: Record<string, string> = {
          new: 'Yeni',
          confirmed: 'Onaylandı',
          preparing: 'Hazırlanıyor',
          shipped: 'Kargoda',
          delivered: 'Teslim Edildi',
          cancelled: 'İptal',
        }
        return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>
      },
    },
  ]

  if (statsLoading || ordersLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <Row gutter={[16, 16]} className="mb-6">
        {statCards.map((card, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card className={`${card.color} border-0`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm mb-1">{card.title}</p>
                  <Statistic
                    value={card.value}
                    prefix={card.prefix}
                    valueStyle={{ fontSize: '24px', fontWeight: 'bold' }}
                  />
                </div>
                {card.icon}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Bugünkü Siparişler" className="shadow-sm">
            <Table
              dataSource={todayOrders || []}
              columns={orderColumns}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Düşük Stok Uyarısı" className="shadow-sm">
            {lowStock?.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Düşük stoklu ürün yok</p>
            ) : (
              <div className="space-y-3">
                {lowStock?.map((product: any) => (
                  <div key={product.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div>
                      <p className="font-medium text-sm">{product.title}</p>
                      <p className="text-xs text-gray-500">SKU: {product.sku}</p>
                    </div>
                    <Tag color="red">{product.stock_quantity} adet</Tag>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
