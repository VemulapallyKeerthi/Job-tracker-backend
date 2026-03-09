FROM python:3.11-slim

# Install ALL system dependencies for Playwright manually
# (playwright install-deps fails on Debian Trixie due to renamed font packages)
RUN apt-get update && apt-get install -y \
    # Core build tools
    wget curl gcc g++ \
    # Chromium dependencies
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    # Fonts (use updated package names for Debian Trixie)
    fonts-liberation \
    fonts-unifont \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser only (skip install-deps — handled above manually)
RUN playwright install chromium

# Copy app source
COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]