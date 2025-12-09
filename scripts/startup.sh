#!/bin/bash
set -e

echo "Starting ETL Service setup..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up - continuing"

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ..."
while ! nc -z rabbitmq 5672; do
  echo "RabbitMQ is unavailable - sleeping"
  sleep 1
done
echo "RabbitMQ is up - continuing"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done
echo "Redis is up - continuing"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Setup completed successfully!"