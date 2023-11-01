# Set timezone
ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime

# Start 
gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --timeout 600 chatbot_app:APP