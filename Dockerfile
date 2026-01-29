FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

# Install all dependencies (Python, Node.js, Git, Build tools)
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    git curl wget \
    libssl-dev libffi-dev build-essential \
    authbind supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ========================================
# INSTALL COWRIE HONEYPOT
# ========================================
WORKDIR /cowrie
RUN git clone https://github.com/cowrie/cowrie.git . && \
    python3 -m venv cowrie-env && \
    . cowrie-env/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install pymongo dnspython && \
    cp etc/cowrie.cfg.dist etc/cowrie.cfg && \
    sed -i 's/listen_endpoints = tcp:2222:interface=127.0.0.1/listen_endpoints = tcp:2222:interface=0.0.0.0/' etc/cowrie.cfg && \
    sed -i 's/listen_endpoints = tcp:2223:interface=127.0.0.1/listen_endpoints = tcp:2223:interface=0.0.0.0/' etc/cowrie.cfg

# ========================================
# SETUP E-COMMERCE APPLICATION
# ========================================
WORKDIR /app

# Copy Python backend files
COPY app.py database.py ecommerce_api.py security_logger.py config.py advanced_security.py ./
COPY templates/ ./templates/
COPY cowrie_to_mongodb.py ./
COPY requirements.txt ./

# Install Python dependencies for Flask
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy and build React frontend
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci --legacy-peer-deps

COPY frontend/ ./
RUN chmod +x node_modules/.bin/* && npm run build

# Move React build to Flask static folder
WORKDIR /app
RUN mkdir -p static && cp -r frontend/dist/* static/

# ========================================
# EXPOSE PORTS  
# ========================================
EXPOSE 2222 2223 5000

# Set working directory
WORKDIR /app

# ========================================
# START APPLICATION
# ========================================
CMD ["python3", "-u", "app.py"]
