# Prapazar Clone - Pazaryeri Entegrasyon Sistemi

Trendyol, Hepsiburada, N11, Gittigidiyor gibi pazaryerlerinde ürün, stok, sipariş yönetimi yapabilen entegrasyon sistemi.

## Özellikler

- ✅ Çoklu pazaryeri desteği (Trendyol, Hepsiburada)
- ✅ Ürün yönetimi (CRUD, varyantlar, görseller)
- ✅ Stok senkronizasyonu (otomatik & manuel)
- ✅ Fiyat yönetimi (pazaryeri özel fiyatlandırma)
- ✅ Sipariş yönetimi (çekme, durum güncelleme, kargo)
- ✅ Kategori eşleştirme
- ✅ Excel ile toplu ürün içe aktarma
- ✅ JWT tabanlı kimlik doğrulama
- ✅ Async API (FastAPI)
- ✅ Arka plan görevleri (Celery + Redis)

## Kurulum

### 1. Gereksinimler
- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### 2. Sanal Ortam
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ortam Değişkenleri
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

### 4. Veritabanı
```bash
# Tabloları oluştur
python -c "import asyncio; from main import lifespan; from app.db.database import create_tables; asyncio.run(create_tables())"

# Veya Alembic ile
alembic upgrade head
```

### 5. Uygulamayı Çalıştır
```bash
# Geliştirme
uvicorn main:app --reload

# Üretim
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Celery Worker
```bash
celery -A app.tasks.sync_tasks worker --loglevel=info
celery -A app.tasks.sync_tasks beat --loglevel=info  # Zamanlanmış görevler
```

## API Dokümantasyonu

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

## Lisans
MIT
