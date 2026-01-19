#!/bin/sh
# Replace placeholder in nginx config with actual API key
sed -i "s|API_KEY_PLACEHOLDER|${API_KEY:-dev-api-key-change-me}|g" /etc/nginx/nginx.conf
exec nginx -g 'daemon off;'
