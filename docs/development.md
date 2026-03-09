# Development Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Development Setup](#development-setup)
5. [Running Tests](#running-tests)
6. [Creating Migrations](#creating-migrations)
7. [Code Style](#code-style)
8. [Adding New Features](#adding-new-features)

---

## Project Overview

**ADA Bali Events** is a community event management platform built for the Apple Developer Academy @ Binus Bali 2026 cohort (approximately 220 students). The platform replaces WhatsApp-based RSVP with a modern, mobile-friendly web application.

### Key Problems Solved

| Problem | Solution |
|---------|----------|
| Manual copy-paste RSVP in WhatsApp | One-click RSVP system |
| No event history | Past events archive |
| Disorganized event categories | Categorized events with filters |
| No photo sharing | Gallery links for post-event photos |
| Communication scattered | WhatsApp group integration |

---

## Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 5.x | Web framework |
| Python | 3.12 | Programming language |
| PostgreSQL | 16 | Primary database |

### Frontend

| Technology | Purpose |
|------------|---------|
| Tailwind CSS | Styling (via CDN for simplicity) |
| Django Templates | Server-side rendering |
| JavaScript | Minimal client-side interactivity |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Nginx | Reverse proxy |
| Gunicorn | WSGI application server |
| GitHub Actions | CI/CD |

---

## Project Structure

```
ada-events/
├── ada_events/              # Django project configuration
│   ├── __init__.py
│   ├── settings.py         # Main settings
│   ├── test_settings.py    # Test settings (SQLite)
│   ├── urls.py             # Root URL configuration
│   ├── wsgi.py             # WSGI entry point
│   └── asgi.py             # ASGI entry point
├── users/                  # User application
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # User model
│   ├── views.py            # User views
│   ├── urls.py             # User URL patterns
│   ├── tests.py            # User tests
│   ├── conftest.py         # Test fixtures
│   └── templates/
│       └── users/          # User templates
├── events/                 # Events application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # Event, RSVP, Category models
│   ├── views.py            # Event views
│   ├── urls.py
│   ├── tests.py
│   ├── conftest.py
│   ├── migrations/         # Database migrations
│   └── templates/
│       └── events/
├── templates/              # Base templates
│   └── base.html          # Base template with nav/footer
├── static/                 # Static files (CSS, JS)
├── media/                  # User-uploaded files
│   ├── profiles/           # Profile photos
│   ├── events/             # Event cover images
│   └── attachments/        # Event attachments
├── nginx/                  # Nginx configuration
│   └── nginx.conf
├── docs/                   # Documentation
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions workflow
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Django app Docker image
├── requirements.txt        # Python dependencies
├── pytest.ini             # Pytest configuration
├── .env.example           # Environment variables template
└── README.md              # Quick start guide
```

---

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Docker and Docker Compose (for full stack)
- PostgreSQL (optional, for local development without Docker)

### Local Development Without Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ada-events
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-django
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Local Development With Docker

1. **Clone and set up**
   ```bash
   git clone <repository-url>
   cd ada-events
   cp .env.example .env
   ```

2. **Edit .env file**
   ```bash
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   POSTGRES_PASSWORD=postgres
   ```

3. **Build and run**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - Open http://localhost:8080
   - Admin panel: http://localhost:8080/admin

---

## Running Tests

This project follows Test-Driven Development (TDD). All new features must have tests.

### Run All Tests

```bash
pytest
```

Current baseline: **53 passing tests**.

### Run Specific Test Files

```bash
# User tests
pytest users/tests.py

# Event tests
pytest events/tests.py
```

### Run Tests with Coverage

```bash
pytest --cov=users --cov=events --cov-report=html
```

### Test Database

Tests use SQLite in-memory database for speed. Configuration is in `ada_events/test_settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
```

### Feature-Specific Test Targets

```bash
# Waitlist / capacity / RSVP
pytest events/tests.py::TestRSVPWaitlistFlow -q

# Search / rate limit / attachments / gallery restriction
pytest events/tests.py::TestEventDiscoveryAndValidation -q

# Notifications inbox
pytest users/tests.py::TestNotificationsViews -q

# Reminder command
pytest events/tests.py::TestReminderCommand -q
```

---

## Creating Migrations

### After Model Changes

Whenever you modify models.py, create migrations:

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### With Docker

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## Code Style

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use Black for formatting: `black .`
- Use isort for imports: `isort .`

### Django

- Use function-based views for simplicity
- Follow Django naming conventions
- Add docstrings to models and views

### Templates

- Use Tailwind CSS classes
- Keep templates in `templates/` directory within each app
- Use descriptive variable names

### Git Commit Messages

Use conventional commits:

```
feat: add event gallery feature
fix: resolve RSVP not saving issue
docs: update deployment guide
test: add tests for user model
```

---

## Adding New Features

### TDD Workflow

1. **Write failing tests first**
   ```bash
   # Create test in tests.py
   pytest path/to/test.py::TestClass::test_name
   # Verify it fails
   ```

2. **Implement minimum code to pass**
   - Add model fields
   - Add views
   - Add URLs

3. **Verify tests pass**
   ```bash
   pytest
   ```

4. **Refactor if needed**
   - Keep tests green
   - Clean up code

### Example: Adding a New Model

1. **Define model in `models.py`**
   ```python
   class Tag(models.Model):
       name = models.CharField(max_length=50)
       event = models.ForeignKey(Event, related_name='tags')
   ```

2. **Write tests in `tests.py`**
   ```python
   def test_create_tag(self):
       tag = Tag.objects.create(name='urgent', event=event)
       assert tag.name == 'urgent'
   ```

3. **Create migration**
   ```bash
   python manage.py makemigrations
   ```

4. **Add to admin if needed**
   ```python
   @admin.register(Tag)
   class TagAdmin(admin.ModelAdmin):
       list_display = ['name', 'event']
   ```

### Example: Adding a New View

1. **Write test first**
   ```python
   def test_event_list_view(self, client):
       response = client.get('/events/')
       assert response.status_code == 200
   ```

2. **Add URL**
   ```python
   path('events/', views.event_list, name='event_list'),
   ```

3. **Implement view**
   ```python
   def event_list(request):
       events = Event.objects.all()
       return render(request, 'events/list.html', {'events': events})
   ```

4. **Create template**
   ```html
   {% extends 'base.html' %}
   {% block content %}
     {% for event in events %}
       {{ event.title }}
     {% endfor %}
   {% endblock %}
   ```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | Check Python path, activate venv |
| Database errors | Run migrations |
| Static files 404 | Run `collectstatic` |
| Port already in use | Stop other servers or use different port |

### Debug Mode

Set in `.env`:
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Reset Database

```bash
# Development (SQLite)
rm db.sqlite3
python manage.py migrate

# Docker
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```
