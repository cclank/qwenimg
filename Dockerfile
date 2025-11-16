# Multi-stage build for QwenImg

# Stage 1: Build frontend
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python backend
FROM python:3.10-slim as backend-builder
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final image
FROM python:3.10-slim
WORKDIR /app

# Install dependencies
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY backend/ ./backend/
COPY qwenimg/ ./qwenimg/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create outputs directory
RUN mkdir -p /app/outputs

# Environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

WORKDIR /app/backend

EXPOSE 8000

CMD ["python", "run.py"]
