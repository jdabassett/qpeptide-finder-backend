#!/bin/bash
set -e

# Determine environment
ENVIRONMENT=${ENVIRONMENT:-development}
echo "🌍 Environment: $ENVIRONMENT"

# MySQL hostname - defaults to 'mysql' for Docker Compose, but can be overridden
MYSQL_HOST=${MYSQL_HOST:-mysql}
echo "🔌 MySQL host: $MYSQL_HOST"

# Function to wait for MySQL server using root credentials
wait_for_mysql() {
    local max_attempts=3
    local attempt=1

    echo "🔄 Waiting for MySQL server to be ready..."

    while [ $attempt -le $max_attempts ]; do
        # Simple root connection test (no app config needed)
        if python3 << 'PYTHON_SCRIPT'
import os
import sys
from sqlalchemy import create_engine, text

root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'rootpassword')
mysql_host = os.getenv('MYSQL_HOST', 'mysql')
root_url = f'mysql+pymysql://root:{root_password}@{mysql_host}:3306/mysql'

try:
    engine = create_engine(root_url, connect_args={'connect_timeout': 3})
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    sys.exit(0)
except Exception as e:
    print(f'Connection attempt failed: {e}', file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
        then
            echo "✅ MySQL server is ready"
            return 0
        fi

        echo "⏳ Waiting for MySQL server... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ MySQL server not ready after $max_attempts attempts"
    echo "💡 Last error:"
    python3 << 'PYTHON_SCRIPT'
import os
from sqlalchemy import create_engine, text
root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'rootpassword')
mysql_host = os.getenv('MYSQL_HOST', 'mysql')
root_url = f'mysql+pymysql://root:{root_password}@{mysql_host}:3306/mysql'
try:
    engine = create_engine(root_url, connect_args={'connect_timeout': 2})
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
except Exception as e:
    print(f'  {e}')
PYTHON_SCRIPT
    return 1
}

# Function to create database (local only)
create_database_if_needed() {
    if [ "$ENVIRONMENT" != "development" ]; then
        echo "⏭️  Skipping database creation (production environment)"
        return 0
    fi

    echo "🗄️  Ensuring database exists and user has permissions (local development)..."

    python3 << 'PYTHON_SCRIPT'
import os
from sqlalchemy import create_engine, text

# Get configuration from environment
db_name = os.getenv('DB_NAME', 'qpeptide-db')
db_user = os.getenv('MYSQL_USER', 'qpeptide_user')
root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'rootpassword')
mysql_host = os.getenv('MYSQL_HOST', 'mysql')
root_url = f'mysql+pymysql://root:{root_password}@{mysql_host}:3306/mysql'

try:
    engine = create_engine(root_url, connect_args={'connect_timeout': 10})
    with engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
        exists = result.fetchone() is not None

        if not exists:
            print(f'📦 Creating database: {db_name}')
            conn.execute(text(f'CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'))
            conn.commit()
            print(f'✅ Database {db_name} created')
        else:
            print(f'✅ Database {db_name} already exists')

        # Always grant permissions (in case they were revoked or not set)
        print(f'🔐 Ensuring user {db_user} has permissions on {db_name}...')
        conn.execute(text(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'%'"))
        conn.execute(text('FLUSH PRIVILEGES'))
        conn.commit()
        print(f'✅ Permissions granted to {db_user} for {db_name}')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT
}

# Function to verify database connection
verify_connection() {
    echo "🔍 Verifying database connection..."

    python3 << 'PYTHON_SCRIPT'
import os
import sys
from app.core.config import settings
from sqlalchemy import create_engine, text

try:
    engine = create_engine(settings.DATABASE_URL, connect_args={'connect_timeout': 10})
    with engine.connect() as conn:
        result = conn.execute(text('SELECT DATABASE(), VERSION()'))
        row = result.fetchone()
        print(f'✅ Connected to database: {row[0]}')
        print(f'   MySQL Version: {row[1]}')
    sys.exit(0)
except Exception as e:
    print(f'❌ Connection failed: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
}

# Main execution
echo "🚀 Starting database initialization..."

# Step 1: Wait for MySQL server
if ! wait_for_mysql; then
    echo "❌ Failed to connect to MySQL server"
    exit 1
fi

# Step 2: Create database (local only)
create_database_if_needed

# Step 3: Verify connection to target database
if ! verify_connection; then
    echo "❌ Failed to connect to target database"
    exit 1
fi

# Step 4: Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Step 5: Final connection verification
echo "🔍 Final connection check..."
verify_connection

echo "✅ Database initialization complete"
echo "🚀 Starting application..."
exec "$@"
