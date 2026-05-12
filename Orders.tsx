import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import trTR from 'antd/locale/tr_TR'
import dayjs from 'dayjs'
import 'dayjs/locale/tr'
import App from './App'
import './index.css'

dayjs.locale('tr')

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={trTR} theme={{ token: { colorPrimary: '#2563eb' } }}>
        <App />
      </ConfigProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)
