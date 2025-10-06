# Nginx Dockerfile for Smart News Aggregator
FROM nginx:1.25-alpine

# Copy nginx configuration
COPY infrastructure/nginx/nginx.conf /etc/nginx/nginx.conf

# Create log directory
RUN mkdir -p /var/log/nginx

# Create SSL directory for certificates (optional)
RUN mkdir -p /etc/nginx/ssl

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
