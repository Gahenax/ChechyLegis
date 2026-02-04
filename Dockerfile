# Production Dockerfile for LEGISCHECHY
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment Defaults
ENV PORT=8000
ENV FILES_ROOT=/var/lib/legischechy/files

# Create storage volume directory
RUN mkdir -p /var/lib/legischechy/files

EXPOSE 8000

# Run entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
