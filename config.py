# Prapazar Clone - Pazaryeri Entegrasyon Sistemi

Trendyol, Hepsiburada, N11, Koçtaş, Pazarama, PTT AVM gibi pazaryerlerinde ürün, stok, sipariş yönetimi yapabilen tam entegrasyon sistemi.

## Desteklenen Pazaryerleri

| Platform | API Türü | Durum |
|----------|----------|-------|
| 🔶 **Trendyol** | REST API | ✅ Tam Destek |
| 🟠 **Hepsiburada** | REST API | ✅ Tam Destek |
| 🟣 **N11** | SOAP/XML | ✅ Tam Destek |
| 🔵 **Koçtaş** | REST API | ✅ Tam Destek |
| 🔴 **Pazarama** | REST API (OAuth) | ✅ Tam Destek |
| 🟡 **PTT AVM** | SOAP/XML | ✅ Tam Destek |
| 📦 **Amazon** | REST API | 🔄 Planlanıyor |

## Özellikler

### Ürün Yönetimi
- ✅ Ürün ekleme, düzenleme, silme
- ✅ Varyant yönetimi (renk, beden vb.)
- ✅ Toplu Excel içe aktarma
- ✅ Görsel yönetimi
- ✅ Çoklu platform kategori eşleştirme

### Stok & Fiyat Senkronizasyonu
- ✅ Otomatik stok senkronizasyonu (tüm platformlar)
- ✅ Pazaryeri özel fiyatlandırma
- ✅ Düşük stok uyarıları
- ✅ Toplu fiyat güncelleme

### Sipariş Yönetimi
- ✅ Otomatik sipariş çekme (tüm platformlar)
- ✅ Sipariş durumu takibi
- ✅ Kargo bilgisi gönderme
- ✅ Sipariş iptali
- ✅ İstatistikler ve raporlar

### Mağaza Yönetimi
- ✅ 6+ pazaryeri desteği
- ✅ API bağlantı testi
- ✅ Manuel senkronizasyon
- ✅ Komisyon oranı ayarı

## Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Frontend | React 18, TypeScript, Tailwind CSS, Ant Design |
| Veritabanı | PostgreSQL 15 |
| Cache & Queue | Redis 7, Celery |
| Container | Docker, Docker Compose |

## Hızlı Başlangıç

### Docker ile (Önerilen)
```bash
# 1. Projeyi klonlayın
git clone <repo-url>
cd prapazar_clone

# 2. .env dosyasını düzenleyin (API key'lerinizi ekleyin)
nano backend/.env

# 3. Docker Compose ile başlatın
docker-compose up -d

# 4. Uygulamaya erişin
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manuel Kurulum

#### Backend
```bash
cd backend

# Sanal ortam
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıklar
pip install -r requirements.txt

# Veritabanı (PostgreSQL kurulu olmalı)
# .env dosyasını düzenleyin

# Tabloları oluştur
python -c "import asyncio; from app.db.database import create_tables; asyncio.run(create_tables())"

# Uygulamayı çalıştır
uvicorn main:app --reload

# Celery worker (başka terminalde)
celery -A app.tasks.sync_tasks worker --loglevel=info

# Celery beat (zamanlanmış görevler için)
celery -A app.tasks.sync_tasks beat --loglevel=info
```

#### Frontend
```bash
cd frontend

# Bağımlılıklar
npm install

# Geliştirme sunucusu
npm run dev

# Üretim derlemesi
npm run build
```

## API Dokümantasyonu

Uygulama çalıştığında:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoint'leri

### Kimlik Doğrulama
- `POST /api/v1/auth/register` - Kayıt
- `POST /api/v1/auth/login` - Giriş
- `GET /api/v1/auth/me` - Profil

### Mağazalar
- `GET /api/v1/stores` - Listele
- `POST /api/v1/stores` - Ekle
- `POST /api/v1/stores/{id}/test-connection` - Bağlantı testi
- `POST /api/v1/stores/{id}/sync` - Senkronize et

### Ürünler
- `GET /api/v1/products` - Listele
- `POST /api/v1/products` - Ekle
- `PUT /api/v1/products/{id}` - Güncelle
- `POST /api/v1/products/import-excel` - Excel içe aktar
- `POST /api/v1/products/{id}/sync/{store_id}` - Pazaryerine gönder

### Siparişler
- `GET /api/v1/orders` - Listele
- `GET /api/v1/orders/stats` - İstatistikler
- `POST /api/v1/orders/{id}/shipment` - Kargo bilgisi
- `POST /api/v1/orders/{id}/cancel` - İptal et

## Pazaryeri API Bilgileri

### Trendyol
1. Satıcı Paneli → Entegrasyon → API bilgileri
2. API Key, API Secret, Satıcı ID alın

### Hepsiburada
1. `saticidestek@hepsiburada.com` adresine mail atın
2. API Key ve Secret talep edin

### N11
1. Satıcı Paneli → Ayarlar → API bilgileri
2. App Key ve App Secret alın

### Koçtaş
1. Satıcı Paneli → Entegrasyon → API erişimi
2. API Key talep edin

### Pazarama
1. Satıcı Paneli → Entegrasyon → API bilgileri
2. Client ID ve Client Secret alın

### PTT AVM
1. Satıcı Paneli → Ayarlar → API bilgileri
2. Kullanıcı adı, şifre ve mağaza kodu alın

## Klasör Yapısı

```
prapazar_clone/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/      # API endpoint'leri
│   │   ├── core/               # Config, Security
│   │   ├── crud/               # CRUD işlemleri
│   │   ├── db/                 # Veritabanı
│   │   ├── models/             # SQLAlchemy modelleri
│   │   ├── schemas/            # Pydantic şemaları
│   │   ├── services/platforms/ # 6+ pazaryeri API servisi
│   │   ├── tasks/              # Celery async görevleri
│   │   └── utils/              # Yardımcı fonksiyonlar
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React bileşenleri
│   │   ├── pages/              # 8+ sayfa
│   │   ├── services/           # API servisleri
│   │   └── store/              # Zustand store
│   └── package.json
└── docker-compose.yml
```

## Lisans
MIT License
