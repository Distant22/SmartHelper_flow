# Set timezone
ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime

# Start 
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 chatbot_app:app
