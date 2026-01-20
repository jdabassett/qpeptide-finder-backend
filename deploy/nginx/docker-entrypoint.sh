#!/bin/sh
# Copy nginx config to writable location and replace placeholder with actual API key
cp /etc/nginx/nginx.conf /tmp/nginx.conf
sed -i "s|API_KEY_PLACEHOLDER|${API_KEY:-dev-api-key-change-me}|g" /tmp/nginx.conf
exec nginx -g 'daemon off;' -c /tmp/nginx.conf
