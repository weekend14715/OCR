#!/bin/bash
# Start script for License Server on Render.com

echo "🚀 Starting OCR License Server..."

# Initialize database if not exists
echo "📦 Initializing database..."
python -c "from app import init_db; init_db(); print('✅ Database initialized')"

# Start Gunicorn server
echo "🌐 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:${PORT:-10000} \
    --workers ${WORKERS:-2} \
    --threads ${THREADS:-4} \
    --timeout ${TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app

