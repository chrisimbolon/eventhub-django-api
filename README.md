#  EventHub Django API

A comprehensive Event Management API built with Django REST Framework for managing technical conferences, sessions, speakers, and attendee registrations.

Caddy + Docker + Django + React — fully HTTPS and modular-monolith (services run on single server)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

## ✨ Features

### Core Functionality
- **Event Management**: Create, update, and manage technical events with capacity tracking
- **Session Scheduling**: Schedule sessions with automatic conflict detection
- **Speaker Management**: Manage speaker profiles and session assignments
- **Track Organization**: Organize sessions into tracks (Backend, Frontend, DevOps, etc.)
- **Attendee Registration**: Handle registrations with capacity enforcement and duplicate prevention
- **JWT Authentication**: Secure API endpoints with JSON Web Tokens
- **Role-Based Permissions**: Different access levels for attendees, organizers, and admins

### Advanced Features
- **Smart Filtering**: Advanced search and filtering capabilities
- **Rate Limiting**: API rate limiting (100 req/hour for anonymous, 1000 req/hour for authenticated)
- **Auto-generated API Docs**: Interactive Swagger UI and ReDoc documentation
- **Conflict Detection**: Automatic session scheduling conflict prevention
- **Capacity Management**: Real-time event capacity tracking
- **Date Validation**: Comprehensive date validation for events and sessions

## 🛠 Tech Stack

### Backend
- **Django 5.0.8** - Web framework
- **Django REST Framework 3.14** - API framework
- **PostgreSQL 15** - Database
- **JWT Authentication** - djangorestframework-simplejwt
- **drf-spectacular** - API documentation
- **Gunicorn** - WSGI server

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query** - State management
- **Axios** - HTTP client

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Caddy** - Reverse proxy
- **GitHub Actions** - CI/CD
- **Redis** - Caching (production)

## 🏗 Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│    Caddy     │─────▶│   Backend   │
│   (React)   │      │ Reverse Proxy│      │  (Django)   │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                   │
                                            ┌──────▼──────┐
                                            │  PostgreSQL │
                                            └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- (Optional) Python 3.11+ and Node.js 20+ for local development

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/chrisimbolon/eventhub-django-api
cd eventhub-django-api
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Start the application**
```bash
docker-compose up --build
```

4. **Run migrations**
```bash
docker-compose exec backend python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. **Access the application**
- Frontend: http://localhost:5173
- API: http://localhost:8000/api/v1
- Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs

## 📚 API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "attendee"
}
```

#### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123"
}
```

### Event Endpoints

#### List Events
```http
GET /api/v1/events/
GET /api/v1/events/?status=published&city=Jakarta
GET /api/v1/events/?is_upcoming=true&registration_open=true
```

#### Create Event
```http
POST /api/v1/events/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Django Conference 2025",
  "slug": "django-conf-2025",
  "description": "Annual Django conference",
  "event_type": "conference",
  "status": "draft",
  "start_date": "2025-11-01T09:00:00Z",
  "end_date": "2025-11-03T18:00:00Z",
  "registration_start": "2025-10-01T00:00:00Z",
  "registration_end": "2025-10-28T23:59:59Z",
  "venue_name": "Jakarta Convention Center",
  "venue_address": "Jl. Gatot Subroto, Jakarta",
  "city": "Jakarta",
  "country": "Indonesia",
  "capacity": 500
}
```

#### Get Event Details
```http
GET /api/v1/events/{slug}/
```

#### Update Event
```http
PUT /api/v1/events/{slug}/
Authorization: Bearer {token}
```

#### Delete Event
```http
DELETE /api/v1/events/{slug}/
Authorization: Bearer {token}
```

### Session Endpoints

#### Create Session
```http
POST /api/v1/sessions/
Authorization: Bearer {token}
Content-Type: application/json

{
  "event": 1,
  "track": 2,
  "title": "Building Scalable APIs with Django",
  "slug": "building-scalable-apis",
  "description": "Learn best practices for building APIs",
  "session_format": "talk",
  "level": "intermediate",
  "start_time": "2025-11-01T10:00:00Z",
  "end_time": "2025-11-01T11:00:00Z",
  "duration_minutes": 60,
  "room": "Hall A",
  "speaker_ids": [1, 2]
}
```

#### List Sessions
```http
GET /api/v1/sessions/
GET /api/v1/sessions/?event=1&track=2
GET /api/v1/sessions/ongoing/
GET /api/v1/sessions/upcoming/
```

### Registration Endpoints

#### Register for Event
```http
POST /api/v1/registrations/
Authorization: Bearer {token}
Content-Type: application/json

{
  "event": 1,
  "dietary_requirements": "Vegetarian",
  "special_requests": "Need wheelchair access"
}
```

#### List My Registrations
```http
GET /api/v1/registrations/
Authorization: Bearer {token}
```

#### Cancel Registration
```http
POST /api/v1/registrations/{id}/cancel/
Authorization: Bearer {token}
```

For complete API documentation, visit `/api/docs/` after starting the server.

## 🧪 Testing

### Run tests
```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=apps --cov-report=html

# Run specific test file
docker-compose exec backend pytest apps/events/tests/test_models.py
```

### Test Coverage Goals
- Models: 90%+
- Views: 85%+
- Serializers: 85%+
- Overall: 85%+

## 🚢 Deployment

### Production Deployment (Using DigitalOcean droplet server)

1. **Prepare server**
```bash
# SSH into your server
ssh root@your-server-ip

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Clone and configure**
```bash
git clone https://github.com/yourusername/eventhub-django-api.git
cd eventhub-api
cp .env.example .env.production
# Edit .env.production with production values
```

3. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### GitHub Actions CI/CD

The project includes automated CI/CD:
- **CI Pipeline**: Runs tests, linting, and builds on every push
- **Deployment**: Automatically deploys to production on push to main branch

Configure these secrets in GitHub:
- `SSH_PRIVATE_KEY`: SSH key for server access
- `SERVER_IP`: Your server IP address
- `SERVER_USER`: SSH username

## 📁 Project Structure

```
eventhub-api/
├── backend/
│   ├── apps/
│   │   ├── events/          # Event management
│   │   ├── sessions/        # Session management
│   │   ├── tracks/          # Track management
│   │   └── users/           # User authentication
│   ├── eventmaster/
│   │   ├── settings/        # Split settings
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── requirements/        # Split requirements
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── Dockerfile
├── Caddyfile
│   ├
│   └── Dockerfile
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

## 🔐 Security Features

- JWT-based authentication
- Rate limiting on API endpoints
- CORS configuration
- SQL injection protection (Django ORM)
- XSS protection
- CSRF protection
- Password validation
- HTTPS enforcement (production)
- Role-based access control

## 🎯 Design Decisions

### Database Schema
- **Normalization**: Followed 3NF for optimal data structure
- **Indexing**: Strategic indexes on frequently queried fields (dates, status, city)
- **Constraints**: Database-level constraints for data integrity
- **Cascading**: Proper CASCADE/SET_NULL for referential integrity

### API Design
- **RESTful**: Following REST principles
- **Versioning**: API versioned at /api/v1/
- **Pagination**: Default 20 items per page
- **Filtering**: Advanced filtering on all list endpoints
- **Serializer Strategy**: Different serializers for list/detail/create operations

### Performance Optimizations
- **Query Optimization**: select_related() and prefetch_related() to reduce N+1 queries
- **Connection Pooling**: Database connection pooling in production
- **Caching**: Redis caching for production
- **Static File Compression**: Caddy compression for static files

### Code Organization
- **App Structure**: Each domain (events, sessions, tracks) is a separate Django app
- **Split Settings**: Development/production settings separation
- **Split Requirements**: Base/dev/production requirements separation
- **Custom Permissions**: Reusable permission classes

## 🐛 Known Limitations & Future Improvements

### Current Limitations
- No email notifications (yet)
- No payment integration
- No real-time updates (WebSocket)
- No social authentication

### Planned Features
- [ ] Email notifications for registrations
- [ ] Payment integration (Stripe/PayPal)
- [ ] QR code generation for tickets
- [ ] Check-in system for attendees
- [ ] Session feedback and ratings
- [ ] Export attendee lists (CSV/Excel)
- [ ] Event analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Real-time session updates via WebSocket
- [ ] Integration with calendar apps (Google Calendar, Outlook)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 🔧 Troubleshooting

### Common Issues

**1. Database connection error**
```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db
```

**2. Migration issues**
```bash
# Reset migrations (development only!)
docker-compose exec backend python manage.py migrate --fake-zero
docker-compose exec backend python manage.py migrate
```

**3. Permission denied errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

**4. Port already in use**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

## 📊 Performance Benchmarks

| Endpoint | Response Time | Throughput |
|----------|--------------|------------|
| GET /events/ | ~50ms | 500 req/s |
| POST /events/ | ~80ms | 300 req/s |
| GET /sessions/ | ~45ms | 550 req/s |
| POST /registrations/ | ~100ms | 250 req/s |

*root.crt settings is needed for TLS smoothnes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Christyan Simbolon**
- GitHub: [@chrisimbolon](https://github.com/chrisimbolon)
- Portfolio: [chrisimbolon.dev](https://chrisimbolon.dev)


## 🙏 Acknowledgments

- Django REST Framework documentation
- React and Vite communities
- TailwindCSS for amazing utility classes
- All open-source contributors

## 📸 Screenshots

### API Documentation (Swagger UI)
![API Docs](docs/screenshots/api-docs.png)

For questions or issues, please open an issue on GitHub or contact me directly.