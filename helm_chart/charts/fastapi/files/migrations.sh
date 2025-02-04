#!/bin/sh 

set -xe


# Function to check if the database is available
check_db() {
    # Replace 'localhost', 'your_db_port', 'your_db_user', 'your_db_password', 'your_db_name' with actual values
    if nc -z postgres 5432; then
        return 0
    else
        return 1
    fi
}

# Wait for database to be available
echo "Waiting for database to become available..."
while ! check_db; do
    echo "Database is not available yet, retrying in 5 seconds..."
    sleep 5
done
echo "Database is now available."

# Ensure the migrations directory exists
if [ ! -d "/home/fastapi/migrations" ]; then
    echo "Error: Migrations directory does not exist at /home/fastapi/migrations"
    exit 1
fi

# Copy application directory to migrations directory
cp -r /home/fastapi/app /home/fastapi/migrations/

# Change to the migrations directory
cd /home/fastapi/migrations 

# Check if the alembic directory exists
if [ ! -d "/home/fastapi/migrations/alembic" ]; then
    echo "Alembic directory not found, initializing..."
    alembic init alembic
    
    # Optionally, you might want to adjust alembic.ini here
    # For example, setting the SQLAlchemy URL:
    # sed -i 's/sqlalchemy.url = .*$/sqlalchemy.url = postgresql:\/\/username:password@localhost\/dbname/' alembic.ini
else
    echo "Alembic directory found, proceeding with migrations."
fi

cp -r /home/fastapi/env.py /home/fastapi/migrations/alembic/

# Run alembic commands for migration
# Here you would put commands like:
# Check if migrations are required
    if alembic check; then
        echo "No migrations needed."
    else
        echo "************************************"
        alembic revision --autogenerate -m "Migration performed at: $(date +%F-%H-%M-%S)"
        echo "************************************"
        alembic upgrade head
    fi

echo "************************************"
echo "Revision history:"
alembic history
echo "************************************"
echo "Migration process completed."
sleep 1