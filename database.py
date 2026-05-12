services:
  # PostgreSQL Database
  - type: pserv
    name: prapazar-db
    runtime: docker
    env: docker
    dockerfilePath: ./docker/postgres.Dockerfile
    envVars:
      - key: POSTGRES_USER
        value: prapazar
      - key: POSTGRES_PASSWORD
        generateValue: true
      - key: POSTGRES_DB
        value: prapazar_db
    disk:
      name: postgres-data
      mountPath: /var/lib/postgresql/data
      sizeGB: 1

  # Redis Cache
  - type: pserv
    name: prapazar-redis
    runtime: docker
    image:
      url: redis:7-alpine
    disk:
      name: redis-data
      mountPath: /data
      sizeGB: 1

  # Backend API
  - type: web
    name: prapazar-backend
    runtime: python
    plan: free
    buildCommand: |
      cd backend
      pip install -r requirements.txt
    startCommand: |
      cd backend
      uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromService:
          name: prapazar-db
          type: pserv
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: prapazar-redis
          type: pserv
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: TRENDYOL_API_KEY
        sync: false
      - key: TRENDYOL_API_SECRET
        sync: false
      - key: HEPSIBURADA_API_KEY
        sync: false
      - key: HEPSIBURADA_API_SECRET
        sync: false
      - key: N11_API_KEY
        sync: false
      - key: N11_API_SECRET
        sync: false
      - key: KOCTAS_API_KEY
        sync: false
      - key: PAZARAMA_API_KEY
        sync: false
      - key: PAZARAMA_API_SECRET
        sync: false
      - key: PTTAVM_API_KEY
        sync: false
      - key: PTTAVM_API_SECRET
        sync: false

  # Celery Worker
  - type: worker
    name: prapazar-celery-worker
    runtime: python
    plan: free
    buildCommand: |
      cd backend
      pip install -r requirements.txt
    startCommand: |
      cd backend
      celery -A app.tasks.sync_tasks worker --loglevel=info --concurrency=2
    envVars:
      - key: DATABASE_URL
        fromService:
          name: prapazar-db
          type: pserv
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: prapazar-redis
          type: pserv
          property: connectionString
      - key: SECRET_KEY
        fromService:
          name: prapazar-backend
          type: web
          property: envVar
          envVarKey: SECRET_KEY
      - key: PYTHON_VERSION
        value: 3.11.0

  # Frontend (Static Site)
  - type: static
    name: prapazar-frontend
    runtime: static
    buildCommand: |
      cd frontend
      npm install
      npm run build
    staticPublishPath: ./frontend/dist
    envVars:
      - key: VITE_API_URL
        fromService:
          name: prapazar-backend
          type: web
          property: url
          envVarKey: API_URL
    routes:
      - type: rewrite
        source: /api/*
        destination: https://prapazar-backend.onrender.com/api/$1
      - type: rewrite
        source: /*
        destination: /index.html
