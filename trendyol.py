version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: prapazar_db
    environment:
      POSTGRES_USER: prapazar
      POSTGRES_PASSWORD: prapazar123
      POSTGRES_DB: prapazar_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U prapazar -d prapazar_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: prapazar_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: prapazar_backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://prapazar:prapazar123@db:5432/prapazar_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=your-super-secret-key-change-in-production
      - DEBUG=False
      - HOST=0.0.0.0
      - PORT=8000
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: prapazar_celery
    environment:
      - DATABASE_URL=postgresql+asyncpg://prapazar:prapazar123@db:5432/prapazar_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=your-super-secret-key-change-in-production
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.tasks.sync_tasks worker --loglevel=info --concurrency=4

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: prapazar_celery_beat
    environment:
      - DATABASE_URL=postgresql+asyncpg://prapazar:prapazar123@db:5432/prapazar_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=your-super-secret-key-change-in-production
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.tasks.sync_tasks beat --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: prapazar_frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
