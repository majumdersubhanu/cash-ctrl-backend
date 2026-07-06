FROM nginx:1.25-alpine

# Install mkcert and CA certificates
RUN apk add --no-cache mkcert ca-certificates

# Generate development certificates
RUN mkcert -install && \
    mkdir -p /etc/nginx/certs && \
    mkcert -cert-file /etc/nginx/certs/nginx.crt -key-file /etc/nginx/certs/nginx.key localhost 127.0.0.1 ::1
