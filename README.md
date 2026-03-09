# ADA Bali Events Platform

A community event management platform for Apple Developer Academy @ Binus Bali 2026 cohort.

## Quick Start

### Local Development

```bash
# Clone and setup
git clone <repo-url>
cd ada-events

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies and build styles
npm install
npm run build

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Open http://localhost

### Frontend Development

To recompile Tailwind CSS while developing:
```bash
npm run watch
```

### With Docker

```bash
cp .env.example .env
# Edit .env with your values
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```

Open http://localhost:8080

## Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/user-guide.md) | How to use the platform |
| [Development Guide](docs/development.md) | Setup & development workflow |
| [Deployment Guide](docs/deployment.md) | Deploy to DigitalOcean |
| [API Reference](docs/api-reference.md) | Models, views, URLs |
| [Google OAuth Guide](docs/google-oauth.md) | Instructions on setting up Google login |
| [Plan](docs/plans/2026-03-08-ada-events-platform-plan.md) | Original design plan |

## Features

- Event creation and management
- RSVP system (Going/Maybe/Can't Go)
- Capacity-aware RSVP with automatic waitlist + promotion
- Categories: Running, Beach, Football, Hiking, Food, Workshop, Social
- Calendar integration (.ics + Google Calendar)
- Event search (title/description/location)
- Attachments upload with validation (type/size/count)
- Gallery links for post-event photos
- WhatsApp group integration
- User profiles
- In-app notifications inbox (mark read / mark all read)
- Reminder command for upcoming events
- Mobile-first design (Apple + Luma style)
- Public/private attendee lists
- Past events archive

## Tech Stack

- Django 5.x
- PostgreSQL
- Tailwind CSS
- Docker
- GitHub Actions

## Tests

```bash
pytest  # All tests
pytest users/tests.py
pytest events/tests.py
```

## Deployment

See [Deployment Guide](docs/deployment.md) for detailed instructions.

## Reminders

```bash
# Dry run
docker compose exec -T web python manage.py send_event_reminders --dry-run

# Real run (next 24h)
docker compose exec -T web python manage.py send_event_reminders --hours-ahead 24
```

## Seed Test Data

```bash
# Example dataset
docker compose exec -T web python manage.py seed_test_data --users 30 --events 50 --rsvps-per-event 8

# Recreate seeded dataset from scratch
docker compose exec -T web python manage.py seed_test_data --reset --users 20 --events 30 --rsvps-per-event 5
```

## License

For ADA @ Binus Bali 2026 Cohort only.
