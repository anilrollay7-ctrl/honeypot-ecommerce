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
COPY app.py database.py ecommerce_api.py security_logger.py config.py ./
COPY templates/ ./templates/
COPY cowrie_to_mongodb.py ./

# Install Python dependencies for Flask
RUN pip3 install --no-cache-dir \
    flask==3.0.0 \
    flask-cors==4.0.0 \
    flask-jwt-extended==4.6.0 \
    pymongo==4.6.1 \
    dnspython==2.4.2 \
    python-dotenv==1.0.0

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
# CREATE STARTUP SCRIPT
# ========================================
RUN echo '#!/bin/bash\n\
set -e\n\
echo "==============================================="\n\
echo "🍯 Starting Unified Honeypot E-commerce System"\n\
echo "==============================================="\n\
echo ""\n\
echo "🔧 Starting Cowrie SSH/Telnet Honeypot..."\n\
cd /cowrie && cowrie-env/bin/python bin/cowrie start\n\
sleep 3\n\
echo "✅ Cowrie started on port 2222 (SSH) and 2223 (Telnet)"\n\
echo ""\n\
echo "📊 Starting MongoDB Attack Logger..."\n\
cd /app && python3 cowrie_to_mongodb.py > /var/log/cowrie-logger.log 2>&1 &\n\
sleep 2\n\
echo "✅ MongoDB logger started"\n\
echo ""\n\
echo "🛒 Starting E-commerce Application (Flask + React)..."\n\
cd /app && python3 app.py\n\
' > /start.sh && chmod +x /start.sh

# ========================================
# EXPOSE PORTS
# ========================================
# Port 2222: SSH Honeypot (Cowrie)
# Port 2223: Telnet Honeypot (Cowrie)
# Port 5000: E-commerce Web Application (Flask + React)
EXPOSE 2222 2223 5000

# ========================================
# START ALL SERVICES
# ========================================
CMD ["/bin/bash", "/start.sh"]
