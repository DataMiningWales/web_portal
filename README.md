# Web Portal for Data Mining Wales

This FastAPI application provides subscription management with AuraDB integration.

## Features

- Subscription POST endpoint with JSON payload handling
- AuraDB integration for data storage
- Duplicate subscription verification
- UID generation for request logging
- Email acknowledgment system for subscription approval/rejection
- Admin interface for authorized database access
- Comprehensive JSON logging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file:
```
NEO4J_URI=neo4j+s://your-auradb-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
SECRET_KEY=your-secret-key
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@dataminingwales.org
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /subscriptions/` - Submit subscription request
- `GET /admin/` - Admin dashboard (requires authentication)
- `GET /admin/subscriptions/` - View all subscriptions (admin only)

## Documentation

Interactive API documentation available at `/docs` when running the application. 
