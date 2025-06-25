FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Adiciona Nginx para mTLS
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copia certificados e configuração do Nginx
COPY keys/server-cert.pem /etc/ssl/certs/server-cert.pem
COPY keys/server-key.pem /etc/ssl/private/server-key.pem
COPY keys/client-cert.crt /etc/ssl/certs/client-cert.crt
COPY keys/client-ca.crt /etc/ssl/certs/client-ca.crt
COPY nginx.conf /etc/nginx/nginx.conf

CMD uvicorn src.api.api:app --host 0.0.0.0 --port 9001 --log-level info & nginx -g 'daemon off;' 