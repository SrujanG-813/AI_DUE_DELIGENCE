# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend package.json and install dependencies
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copy all source code
COPY . .

# Build frontend
RUN cd frontend && npm run build

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "api_server.py"]