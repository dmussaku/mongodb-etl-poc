
# ETL Service

A scalable ETL (Extract, Transform, Load) service for data pipeline management, built with modern Python technologies.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Web Server  │───▶│   Queue     │───▶│  Workers    │
│  (FastAPI)  │    │ (RabbitMQ)  │    │  (Celery)   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                      │
       ▼                                      ▼
┌─────────────┐                        ┌─────────────┐
│ PostgreSQL  │                        │   MongoDB   │
│ (Metadata)  │                        │  (Source)   │ 
└─────────────┘                        └─────────────┘
```

## 🚀 Tech Stack

- **Web Framework**: FastAPI
- **ETL Engine**: dlt (data load tool)
- **Task Queue**: Celery + RabbitMQ
- **Database**: PostgreSQL (metadata), MongoDB (source)
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose

## 📋 Features

### ✅ Current Features
- **Modern React UI** - Clean, responsive Material-UI interface
- **ETL Job Management** - Create, monitor, and manage data pipelines
- **MongoDB Integration** - Full aggregation pipeline support  
- **Data Masking** - Configurable field-level data masking
- **Real-time Monitoring** - Live job status and execution history
- **Health Dashboard** - System health monitoring for all services
- **RESTful API** - Complete API with interactive documentation
- **Scalable Architecture** - Containerized microservices with Docker

### 🔄 Incremental Load Support
- Full and incremental load strategies
- Change detection and delta processing
- Configurable incremental columns

### 🎯 Multiple Destinations  
- PostgreSQL, BigQuery, S3 support via dlt
- Extensible destination framework

## 🛠️ Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd mongodb-etl-poc

# Copy environment file
cp .env.example .env
```

### 2. Start Services

```bash
# Easy start with our script
./start.sh

# Or manually with docker-compose
docker-compose up -d
```

### 3. Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (admin/password)
- **Health Check**: http://localhost:8000/api/v1/health

## 🔧 Development

### Project Structure

```
mongodb-etl-poc/
├── frontend/          # React TypeScript UI
│   ├── src/
│   │   ├── components/    # React components
│   │   └── services/      # API services
│   └── package.json
├── backend/           # FastAPI Python backend
│   ├── src/
│   │   ├── api/           # FastAPI routes
│   │   ├── config/        # Configuration management
│   │   ├── etl/           # ETL pipeline logic
│   │   ├── models/        # Database models
│   │   └── worker/        # Celery tasks
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── worker/            # Celery worker configuration
├── scripts/           # Startup scripts
└── docker-compose.yml # Service orchestration
```

### Database Migrations

```bash
# Create new migration
docker-compose exec web alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec web alembic upgrade head
```

### Testing Celery

```bash
# Test Celery connectivity
curl -X POST "http://localhost:8000/api/v1/test-celery"
```

## 📊 API Endpoints

### Health Check
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed service health

### ETL Jobs
- `GET /api/v1/jobs` - List all ETL jobs
- `GET /api/v1/jobs/{job_id}` - Get job details
- `POST /api/v1/jobs/{job_id}/run` - Trigger manual job run
- `GET /api/v1/jobs/{job_id}/runs` - List job execution history

### Connections
- `GET /api/v1/connections` - List database connections

## 🔍 Monitoring

### View Logs

```bash
# Web application logs
docker-compose logs -f web

# Worker logs
docker-compose logs -f worker

# All services
docker-compose logs -f
```

### Service Health

```bash
# Check all service health
curl http://localhost:8000/api/v1/health/detailed
```

## 🛡️ Security

- Environment-based configuration
- Connection string encryption (TODO)
- API authentication (TODO)
- Role-based access control (TODO)

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Update `.env` with production values
2. **Database**: Use managed PostgreSQL service
3. **Message Broker**: Use managed RabbitMQ/Redis
4. **Scaling**: Increase worker replicas in docker-compose
5. **Monitoring**: Add Prometheus/Grafana integration
6. **Security**: Enable authentication and HTTPS

### Scaling Workers

```yaml
# In docker-compose.yml
worker:
  deploy:
    replicas: 5  # Increase for higher throughput
```

## 📝 Sample Data

Input: Fake people database with various data structures
- Size: 2.6 GB
- Count: 2.2M Documents

Example document structure:
```json
{
  "_id": "ObjectId('...')",
  "person_type": "Student",
  "first_name": "Bradley",
  "last_name": "Choi",
  "email": "example@domain.com",
  "address": {
    "street": "123 Main St",
    "city": "Example City"
  },
  "tags": ["tag1", "tag2"]
}
        "enrolled_at" : ISODate("2020-03-28T02:20:14.929+0000"),
        "finished_at" : null,
        "enrolled_courses" : [
            "83e9ffbb233b4fbb834c66bd253288a5",
            "bda5c36fa92c4020a5a7b6ed5bd3a36a",
            "ed6319c702b34b70b32ef7b30d160fee",
            "fbf50d033b324beea17971cb573e1b26",
            "706d3b4a9946485099785075ec08a2ce",
            "db7c447dce6244598e9b3af58ff1d518",
            "b3da18f425c54e60829e3911919481a3"
        ],
        "major" : "History",
        "minor" : null,
        "gpa" : 2.64,
        "credits_completed" : NumberInt(88),
        "status" : "graduated",
        "international" : false,
        "on_scholarship" : true
    },
    "professor" : null,
    "metadata" : {
        "last_portal_login" : ISODate("2025-08-19T21:00:45.180+0000"),
        "notes" : "",
        "flags" : [
            "housing_waitlist",
            "late_fee"
        ]
    }
}
```


1st case: Mongodb to Mongodb transformation using ingestr with field masking (no data flattening yet)


Command ran:
```
time ingestr ingest \
--source-uri "mongodb://root:password@localhost:27017/" \
--source-table "university.people" \
--dest-uri "mongodb://root:password@localhost:27017/" \
--dest-table "analytics.people_analytics" \
--incremental-strategy append \
  --incremental-key "updated_at" \
  --primary-key "_id" \
--mask "first_name:hash" \
--mask "last_name:hash" \
--mask "full_name:hash" \
--mask "email:email" \
--mask "phone:phone" \
--mask "date_of_birth:year_only" --progress log
```

Success: Successfully finished loading data from 'mongodb' to 'mongodb' in 10 minutes and 28.13 seconds

```
{
    "_id" : "6936dcbf513cd68d0ebb26aa",
    "email" : "c***********r@example.com",
    "address__street" : "20731 Duran Valleys",
    "address__city" : "Smithchester",
    "address__state" : "New Hampshire",
    "address__postal_code" : "48320",
    "address__country" : "Congo",
    "address__geo" : {
        "lat" : 39.686203,
        "lng" : -12.279112
    },
    "created_at" : ISODate("2025-12-08T14:16:23.731+0000"),
    "date_of_birth" : NumberInt(1961),
    "emergency_contacts" : [

    ],
    "first_name" : "62fe4843ff9d2d79c52749cb0073c8490e7e490f03b98911d3acd4661ea69b5b",
    "full_name" : "ce7648f5a3f2f56df1e99e396ea47ba0033099eea3a5f3fba04798e79f8c2e34",
    "last_name" : "3ccea6fa629fb6ad2149312db9403174f15f612f813d9c3e34eb3f15b5d217a7",
    "metadata__last_portal_login" : ISODate("2025-10-02T09:15:47.598+0000"),
    "metadata__notes" : "",
    "metadata__flags" : [
        "housing_waitlist"
    ],
    "person_type" : "Student",
    "phone" : "536-***-****",
    "preferences__newsletter_opt_in" : false,
    "preferences__preferred_contact" : "email",
    "student__student_type" : "PostGrad",
    "student__year_of_study" : "VII",
    "student__enrolled_at" : ISODate("2020-09-16T10:13:42.840+0000"),
    "student__enrolled_courses" : [
        "505c3d4aa04d41f1be7ffeaf62d4be96",
        "4713433ad49e43ca934ff2aef727cbd2",
        "83cb707c5db141c3842fa34706ed7c37",
        "c423276ee6d648eca26fb41b34d6dcae",
        "63c0a6c547a64578bd8917db09804894",
        "cee623bb100f4763ab1a26f005b1f67e",
        "a4264d4e63e34c68ac420d7cfb93eb99"
    ],
    "student__major" : "Chemistry",
    "student__minor" : "Physics",
    "student__gpa" : 2.14,
    "student__credits_completed" : NumberInt(144),
    "student__status" : "dismissed",
    "student__international" : false,
    "student__on_scholarship" : false,
    "tags" : [

    ],
    "updated_at" : ISODate("2025-12-08T14:16:23.731+0000")
}
```



case 2: mongodb to postgres

```
time ingestr ingest \
--source-uri "mongodb://root:password@localhost:27017/" \
--source-table "university.people" \
--dest-uri "postgresql://postgres:password@localhost:5432/" \
--dest-table "etl_db.people_analytics" \
--incremental-strategy append \
  --incremental-key "updated_at" \
  --primary-key "_id" \
--mask "first_name:hash" \
--mask "last_name:hash" \
--mask "full_name:hash" \
--mask "email:email" \
--mask "phone:phone" \
--mask "date_of_birth:year_only"
```

Successfully finished loading data from 'mongodb' to 'postgresql' in 8 minutes and 38.96 seconds



case 3: Mongodb to Mongodb (10 records) unnested + array obfuscation


```
time ingestr ingest \
--source-uri "mongodb://root:password@localhost:27017/" \
--source-table 'university.people:[{"$limit": 10}]' \
--dest-uri "mongodb://root:password@localhost:27017/" \
--dest-table "analytics.people_analytics_10_records" \
--incremental-strategy append \
  --incremental-key "updated_at" \
  --primary-key "_id" \
--mask "first_name:hash" \
--mask "last_name:hash" \
--mask "full_name:hash" \
--mask "email:email" \
--mask "phone:phone" \
--mask "date_of_birth:year_only" \
--mask "address.street:hash" \
--mask "address.geo.lat:stars" \
--mask "address.geo.lng:stars" \
--progress log
```
