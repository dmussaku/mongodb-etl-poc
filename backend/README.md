# Django Celery Task Management System

This project demonstrates a complete Django application with PostgreSQL database, Celery task queue with RabbitMQ broker, Redis as result backend, and Flower for task monitoring.

## Features

- **Django Web Application**: REST API endpoints for task management
- **PostgreSQL Database**: Stores task results and application data
- **Celery Task Queue**: Asynchronous task processing
- **RabbitMQ**: Message broker for Celery
- **Redis**: Result backend for Celery
- **Flower**: Web-based monitoring tool for Celery tasks
- **Docker Compose**: Complete containerized setup

## Services

The application includes the following services:

1. **Django Web App** (Port 8000): Main web application
2. **PostgreSQL** (Port 5432): Database server
3. **RabbitMQ** (Port 5672, Management UI: 15672): Message broker
4. **Redis** (Port 6379): Cache and result backend
5. **Celery Worker**: Background task processor
6. **Flower** (Port 5555): Task monitoring interface

## Quick Start

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f django
   docker-compose logs -f celery-worker
   ```

## Available Endpoints

### Web Interface
- **Task Dashboard**: http://localhost:8000/tasks/
- **Admin Interface**: http://localhost:8000/admin/ (admin/admin123)

### API Endpoints
- `POST /tasks/trigger/foo-bar/` - Trigger foo bar task
  ```json
  {"name": "World"}
  ```

- `POST /tasks/trigger/add/` - Trigger add numbers task
  ```json
  {"x": 5, "y": 10}
  ```

- `POST /tasks/trigger/multiply/` - Trigger multiply numbers task
  ```json
  {"x": 3, "y": 7}
  ```

- `GET /tasks/status/{task_id}/` - Get task status

### Monitoring Interfaces
- **Flower (Celery Monitoring)**: http://localhost:5555/
- **RabbitMQ Management**: http://localhost:15672/ (guest/guest)

## Sample Tasks

The application includes three sample Celery tasks:

1. **foo_bar_task**: A simple greeting task with random delay (5-15 seconds)
2. **add_numbers**: Adds two numbers
3. **multiply_numbers**: Multiplies two numbers with 3-second delay

## Testing the Tasks

### Using the Web Interface
1. Visit http://localhost:8000/tasks/
2. Use the form to trigger different tasks
3. Refresh the page to see results
4. Monitor tasks at http://localhost:5555/

### Using curl
```bash
# Trigger foo bar task
curl -X POST http://localhost:8000/tasks/trigger/foo-bar/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Docker"}'

# Trigger add task
curl -X POST http://localhost:8000/tasks/trigger/add/ \
  -H "Content-Type: application/json" \
  -d '{"x": 15, "y": 25}'

# Check task status (replace with actual task ID)
curl http://localhost:8000/tasks/status/your-task-id-here/
```

## Database Management

### Run Django commands
```bash
# Make migrations
docker-compose exec django python manage.py makemigrations

# Apply migrations
docker-compose exec django python manage.py migrate

# Create superuser
docker-compose exec django python manage.py createsuperuser

# Django shell
docker-compose exec django python manage.py shell
```

### Access PostgreSQL
```bash
docker-compose exec postgres psql -U postgres -d etl_db
```

## Development

### Add new tasks
1. Add your task function to `backend/tasks/tasks.py`
2. Create an endpoint in `backend/tasks/views.py`
3. Add URL pattern in `backend/tasks/urls.py`
4. Update the template if needed

### Environment Variables
Key environment variables (set in docker-compose.yml):
- `DEBUG`: Django debug mode
- `SECRET_KEY`: Django secret key
- `DB_*`: Database connection settings
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL

## Troubleshooting

### Check service health
```bash
docker-compose ps
```

### View service logs
```bash
docker-compose logs celery-worker
docker-compose logs django
```

### Restart services
```bash
docker-compose restart
```

### Clean restart
```bash
docker-compose down
docker-compose up --build
```

### Common Issues

1. **Database connection errors**: Wait for PostgreSQL to be fully ready
2. **Celery tasks not executing**: Check RabbitMQ and worker logs
3. **Permission errors**: Check file permissions and Docker volumes

## Project Structure

```
backend/
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
├── setup.sh               # Initial setup script
├── myproject/             # Django project
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── celery.py         # Celery configuration
└── tasks/                 # Django app for tasks
    ├── __init__.py
    ├── admin.py          # Admin configuration
    ├── apps.py           # App configuration
    ├── models.py         # Database models
    ├── tasks.py          # Celery tasks
    ├── urls.py           # URL patterns
    ├── views.py          # API views
    └── templates/        # HTML templates
        └── tasks/
            └── task_list.html
```

## License

This project is for demonstration purposes.