# Universal Dockerfile - optimized for all platforms
FROM nginx:alpine

LABEL maintainer="Universal EML WebApp"
LABEL description="Cross-platform Dashboard - Faktury Maj 2025"
LABEL platforms="linux/amd64,linux/arm64,windows,macos"

# Create app directory
WORKDIR /usr/share/nginx/html

# Copy all web assets
COPY *.html ./
COPY *.css ./
COPY *.js ./
COPY *.jpg ./
COPY *.json ./

# Create optimized nginx configuration
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Universal CORS and security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    add_header Referrer-Policy "strict-origin-when-cross-origin" always; \
    \
    # Enable CORS for local development \
    add_header Access-Control-Allow-Origin "*" always; \
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always; \
    add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept" always; \
    \
    # Main location block \
    location / { \
        try_files $uri $uri/ /index.html; \
        \
        # Cache control for HTML \
        location ~* \\html$ { \
            expires 1h; \
            add_header Cache-Control "public, must-revalidate"; \
        } \
    } \
    \
    # Static assets with long cache        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
        access_log off; \
    } \
    \
    # JSON files \
    location ~* \.json$ { \
        expires 1h; \
        add_header Content-Type "application/json"; \
    } \
    \
    # Gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types \
        text/plain \
        text/css \
        text/xml \
        text/javascript \
        application/javascript \
        application/json \
        application/xml+rss; \
    \
    # Security: disable server tokens \
    server_tokens off; \
    \
    # Handle favicon requests \
    location = /favicon.ico { \
        access_log off; \
        log_not_found off; \
    } \
    \
    # Health check endpoint \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

# Create health check script
RUN echo '#!/bin/sh\ncurl -f http://localhost/health || exit 1' > /health-check.sh && \
    chmod +x /health-check.sh

# Expose port
EXPOSE 80

# Health check for all platforms
HEALTHCHECK --interval0s --timeouts --start-period=5s --retries=3 \
    CMD /health-check.sh

# Labels for better Docker management
LABEL org.opencontainers.image.title="Universal EML WebApp"
LABEL org.opencontainers.image.description="Cross-platform invoice dashboard"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2025-06-19"

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
