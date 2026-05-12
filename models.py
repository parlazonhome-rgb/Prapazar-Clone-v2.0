# Render.com Deploy Rehberi

## Adım 1: GitHub Repo Oluşturun

```bash
# 1. GitHub'da yeni repo oluşturun (örn: prapazar-clone)

# 2. Projeyi Git'e ekleyin
cd prapazar_clone
git init
git add .
git commit -m "Initial commit - Prapazar Clone v2.0"

# 3. GitHub'a push edin
git remote add origin https://github.com/KULLANICI_ADI/prapazar-clone.git
git branch -M main
git push -u origin main
```

## Adım 2: Render.com'a Kaydolun

1. https://render.com adresine gidin
2. "Get Started for Free" butonuna tıklayın
3. GitHub hesabınızla giriş yapın
4. Render'a GitHub erişimi verin

## Adım 3: Blueprint ile Deploy Edin

### Yöntem A: Blueprint (Önerilen)

1. Render Dashboard'da "New +" → "Blueprint" seçin
2. GitHub repo'nuzu seçin
3. `render.yaml` dosyasını otomatik algılar
4. "Apply" butonuna tıklayın
5. Render otomatik olarak şunları oluşturur:
   - PostgreSQL veritabanı
   - Redis cache
   - Backend API
   - Celery Worker
   - Frontend (Static Site)

### Yöntem B: Manuel Olarak

#### 1. PostgreSQL Veritabanı
```
New + → PostgreSQL
Name: prapazar-db
Database: prapazar_db
User: prapazar
Plan: Free
```

#### 2. Redis
```
New + → Redis
Name: prapazar-redis
Plan: Free
```

#### 3. Backend (Web Service)
```
New + → Web Service
Repo: GitHub repo'nuz
Name: prapazar-backend
Runtime: Python 3
Build Command:
  cd backend && pip install -r requirements.txt
Start Command:
  cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
Plan: Free

Environment Variables:
  DATABASE_URL: (PostgreSQL connection string)
  REDIS_URL: (Redis connection string)
  SECRET_KEY: (rastgele bir string)
  TRENDYOL_API_KEY: (API key'iniz)
  TRENDYOL_API_SECRET: (API secret'ınız)
  HEPSIBURADA_API_KEY: (API key'iniz)
  HEPSIBURADA_API_SECRET: (API secret'ınız)
  N11_API_KEY: (App Key'iniz)
  N11_API_SECRET: (App Secret'ınız)
  KOCTAS_API_KEY: (API key'iniz)
  PAZARAMA_API_KEY: (Client ID'niz)
  PAZARAMA_API_SECRET: (Client Secret'ınız)
  PTTAVM_API_KEY: (Kullanıcı adınız)
  PTTAVM_API_SECRET: (Şifreniz)
```

#### 4. Celery Worker (Background Worker)
```
New + → Background Worker
Repo: GitHub repo'nuz
Name: prapazar-celery
Runtime: Python 3
Build Command:
  cd backend && pip install -r requirements.txt
Start Command:
  cd backend && celery -A app.tasks.sync_tasks worker --loglevel=info
Plan: Free

Environment Variables:
  DATABASE_URL: (PostgreSQL connection string)
  REDIS_URL: (Redis connection string)
  SECRET_KEY: (Backend ile aynı)
```

#### 5. Frontend (Static Site)
```
New + → Static Site
Repo: GitHub repo'nuz
Name: prapazar-frontend
Build Command:
  cd frontend && npm install && npm run build
Publish Directory: frontend/dist
Plan: Free

Environment Variables:
  VITE_API_URL: https://prapazar-backend.onrender.com/api/v1
```

## Adım 4: API Key'lerinizi Ekleyin

Render Dashboard → prapazar-backend → Environment → Add Environment Variable

Her pazaryeri için API bilgilerinizi ekleyin:

| Değişken | Açıklama |
|----------|----------|
| TRENDYOL_API_KEY | Trendyol API Key |
| TRENDYOL_API_SECRET | Trendyol API Secret |
| HEPSIBURADA_API_KEY | Hepsiburada API Key |
| HEPSIBURADA_API_SECRET | Hepsiburada API Secret |
| N11_API_KEY | N11 App Key |
| N11_API_SECRET | N11 App Secret |
| KOCTAS_API_KEY | Koçtaş API Key |
| PAZARAMA_API_KEY | Pazarama Client ID |
| PAZARAMA_API_SECRET | Pazarama Client Secret |
| PTTAVM_API_KEY | PTT AVM Kullanıcı Adı |
| PTTAVM_API_SECRET | PTT AVM Şifre |

## Adım 5: Deploy Edin

1. Her servis için "Manual Deploy" → "Deploy Latest Commit"
2. Deploy loglarını kontrol edin
3. Başarılı olduğunda URL'ler:
   - Frontend: https://prapazar-frontend.onrender.com
   - Backend: https://prapazar-backend.onrender.com
   - API Docs: https://prapazar-backend.onrender.com/docs

## Adım 6: İlk Kullanım

1. Tarayıcıda https://prapazar-frontend.onrender.com açın
2. Kayıt olun (ilk kullanıcı admin olur)
3. Mağazalar sayfasından pazaryeri ekleyin
4. API bağlantı testi yapın
5. Ürünlerinizi ekleyin ve senkronize edin

## Ücretsiz Plan Limitleri

| Servis | Limit |
|--------|-------|
| Web Service | 750 saat/ay, 15 dk uyku |
| Worker | 750 saat/ay |
| PostgreSQL | 1 GB, 90 gün sonra silinir |
| Redis | 25 MB |
| Static Site | 100 GB bant genişliği/ay |

## Sorun Giderme

### "Application Error" görüyorum
- Backend loglarını kontrol edin: Render Dashboard → Logs
- Environment variable'ları doğru girdiğinizden emin olun
- DATABASE_URL ve REDIS_URL doğru mu?

### API bağlantı testi başarısız
- API key'leri doğru girdiğinizden emin olun
- Satıcı ID'nizi kontrol edin
- Pazaryeri hesabınızın API erişimi var mı?

### Frontend backend'e bağlanmıyor
- VITE_API_URL doğru mu?
- CORS_ORIGINS'e frontend URL'si eklenmiş mi?

### Veritabanı bağlantı hatası
- PostgreSQL servisi çalışıyor mu?
- DATABASE_URL doğru mu?

## Önemli Notlar

1. **Ücretsiz PostgreSQL 90 gün sonra silinir** - önemli verilerinizi yedekleyin
2. **Web servis 15 dk kullanılmazsa uyku moduna geçer** - ilk istek yavaş olabilir
3. **Celery worker ücretsiz planda sınırlı** - çok fazla senkronizasyon görevi koymayın
4. **API key'lerinizi asla GitHub'a push etmeyin** - Render Environment Variables kullanın
