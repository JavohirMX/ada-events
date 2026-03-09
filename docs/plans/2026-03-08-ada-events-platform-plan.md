# ADA Bali 2026 Community Events Platform - Detailed Plan

## 1. Project Overview

A private event management platform for Apple Developer Academy @ Binus Bali 2026 cohort (~220 students) to replace WhatsApp-based RSVP. Features event creation, RSVP management, and community engagement with Apple+Luma-inspired design.

**Tech Stack:**
- Backend: Django 5.x
- Database: PostgreSQL (hosted on same DO droplet)
- Frontend: Django Templates + Tailwind CSS
- Admin: Django Admin + Jazzmin
- Auth: Django Allauth (for Google OAuth)
- Deployment: Docker + GitHub Actions to DigitalOcean VPS

---

## 2. Core Features

### 2.1 Authentication & Users
- **Signup**: Google OAuth (optional) OR email/password (no verification required)
- **Profile**: Name, bio, profile photo (upload), WhatsApp link (optional)
- **Landing**: Public page showing upcoming events (login to RSVP)

### 2.2 Events
- **Creation**: Any member can create events
- **Details**: 
  - Title, description, category (hybrid: predefined + custom tags)
  - Date/time, location, location_url (Google Maps)
  - Image (cover), attachments (multiple files)
  - **Gallery** (optional): Link to external photo album (Google Photos, GDrive, Dropbox, etc.) - **only visible and editable AFTER event date has passed**
- **Categories** (predefined): Running, Beach, Football, Hiking, Food, Workshop, Social, Other
- **Visibility**: Public or Private attendee list (creator chooses)
- **Capacity**: Optional max attendees with waitlist
- **RSVP Options**: Going, Maybe, Can't Go
- **RSVP UX**: Maximum 3 clicks to RSVP (one-tap for "Going" from event list)
- **Calendar**: Add to Google Calendar + Download .ics
- **WhatsApp**: Link to event discussion group
- **Archive**: Past events viewable in archive

### 2.3 Event Discovery
- **Home Feed**: All upcoming events sorted by date
- **Filters**: By category, date range
- **Search**: By title, description, location

### 2.4 User Dashboard
- My upcoming events (created + RSVP'd)
- My past events
- My RSVPs overview

### 2.5 Notifications
- In-app notifications for: new events from followed users, event updates
- Event reminders: 24h and 1h before (in-app + browser push if enabled)
- NO email notifications

### 2.6 Admin (Owner)
- Django Admin + Jazzmin for full system management
- Manage users, events, categories
- Site settings

---

## 3. Database Schema

### User (Extended Django User)
- id, email, name, profile_photo, whatsapp_link, bio
- created_at, updated_at

### Event
- id, creator (User FK), title, description, category
- event_date, event_time, location, location_url (Google Maps)
- image, attachments (multiple)
- is_public_attendees, max_attendees
- whatsapp_group_link
- **gallery_link** (optional): URL to external photo album
- created_at, updated_at

### EventCategory
- id, name, icon, color

### RSVP
- id, event (Event FK), user (User FK)
- status: going/maybe/not_going
- created_at

### Waitlist
- id, event (Event FK), user (User FK)
- position, joined_at

### Notification
- id, user (User FK), type, message, link
- is_read, created_at

---

## 4. UI/UX Design

### Style: Apple + Luma Fusion
- **Apple**: Clean typography (SF Pro / system fonts), generous whitespace, subtle shadows, smooth animations, minimal chrome
- **Luma**: Event cards with images, clear CTAs, category tags, attendee avatars

### Color Palette
- Primary: Apple-like neutral (white/black)
- Accent: Coral/Orange (energetic, beach/Bali vibe)
- Category colors: Distinct per type

### Layout
- **Public Landing**: Hero with logo, featured events, CTA to join/RSVP
- **Event List**: Grid of event cards with image, title, date, attendees count
- **Event Detail**: Large image header, clear RSVP buttons, attendee list, calendar actions, gallery link (shown for past events)
- **Profile**: Cover photo, avatar, bio, event history

### Responsive
- Mobile-first design
- Bottom navigation on mobile

---

## 5. Deployment Architecture

```
┌─────────────────────────────────────────┐
│           DigitalOcean VPS              │
│  ┌─────────────────────────────────┐    │
│  │         Docker Compose          │    │
│  │  ┌─────────┐  ┌─────────────┐   │    │
│  │  │  Nginx  │  │  Django     │   │    │
│  │  │ (proxy) │  │  (Gunicorn) │   │    │
│  │  └─────────┘  └─────────────┘   │    │
│  │  ┌─────────┐                     │    │
│  │  │PostgreSQL│                    │    │
│  │  └─────────┘                     │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

**Note**: Using Django's `django-background-tasks` for reminders instead of Celery/Redis to reduce infrastructure complexity.

### GitHub Actions CI/CD
1. Push to main branch
2. Run: lint, test
3. Build Docker image
4. SSH to DO droplet
5. Pull new image, restart containers

---

## 6. Implementation Phases

### Phase 1: Foundation
- Project setup (Django + Tailwind + Docker)
- User auth (email + Google OAuth)
- User profile model + views
- Basic landing page

### Phase 2: Events Core
- Event model + CRUD
- Event categories
- Event detail page
- Event list/filter
- Add gallery_link field to Event model

### Phase 3: RSVP System
- RSVP model + actions
- Attendee list (public/private)
- Waitlist logic
- Calendar integration (.ics + Google Calendar)

### Phase 4: Community Features
- Attachments upload
- WhatsApp link integration
- User dashboard
- Past events archive
- Gallery link management (edit after event)

### Phase 5: Notifications
- In-app notifications
- Event reminders (django-background-tasks)
- Profile/notification settings

### Phase 6: Polish
- UI refinement
- Mobile responsiveness
- Performance optimization
- Documentation

### Phase 7: Deployment
- Docker setup
- PostgreSQL config
- Nginx config
- GitHub Actions pipeline
- DO droplet setup

---

## 7. File Structure

```
/home/jmx/Files/Programming/Projects/events/
├── docker-compose.yml
├── Dockerfile
├── nginx/
│   └── nginx.conf
├── .github/
│   └── workflows/
│       └── deploy.yml
├── requirements.txt
├── manage.py
├── events/                    # Main Django app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── managers.py
│   ├── signals.py
│   ├── management/
│   │   └── commands/
│   │       └── reminders.py   # Background task for reminders
│   ├── migrations/
│   └── templates/
│       └── events/
│           ├── base.html
│           ├── home.html
│           ├── event_list.html
│           ├── event_detail.html
│           ├── event_create.html
│           ├── profile.html
│           └── dashboard.html
├── users/                     # User app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── oauth.py
│   └── templates/
│       └── users/
│           ├── login.html
│           ├── register.html
│           └── profile.html
├── static/
│   └── css/
│       └── output.css
├── media/
│   └── attachments/
├── .env.example
└── README.md
```

---

## 8. Plan Analysis from Different Perspectives

### 8.1 Scalability Perspective
- **Current**: 220 users is small, Django + PostgreSQL handles this easily
- **Growth**: If cohort grows or future cohorts join, system scales horizontally
- **Fix Applied**: Removed Redis/Celery, using `django-background-tasks` instead for reminders - simpler infrastructure
- **Result**: Reduced memory footprint, easier deployment, less moving parts

### 8.2 Security Perspective
- **No email verification**: Acceptable since it's a closed community with shared invite
- **Fix Applied - File uploads**: 
  - Validate file types: images (jpg, png, gif, webp), documents (pdf, doc, docx)
  - Max file size: 10MB per file
  - Max 5 attachments per event
  - Store in media/attachments/ with unique filenames
- **Public/private events**: Clear logic - only show attendee list based on event setting
- **Rate limiting**: Limit RSVP actions to 1 per 5 seconds per user to prevent spam
- **Fix Applied - Django Allauth**: Using established library for secure OAuth handling
- **Fix Applied - CSRF**: All forms protected with Django's built-in CSRF

### 8.3 User Experience Perspective
- **WhatsApp replacement**: Must be faster than copying names in WhatsApp - **target <3 clicks to RSVP**
- **Fix Applied - Quick RSVP**: "Going" button directly on event card (1 click from list view)
- **Mobile-first**: 220 students likely primarily mobile users - prioritize mobile UX
- **Fix Applied - Gallery timing**: Gallery link field only visible/editable after event date has passed
- **PWA**: Consider PWA features for offline event viewing (Phase 6)

### 8.4 Maintenance Perspective
- **Django templates**: Simpler than SPA but harder to maintain at scale - acceptable for 220 users
- **Tailwind**: Good choice for rapid styling
- **Fix Applied - django-background-tasks**: No Redis/Celery complexity - uses database-backed scheduling
- **Django Allauth**: Battle-tested auth library - reduces custom code
- **Jazzmin**: Good for admin, provide custom event management views if needed

### 8.5 Cost Perspective
- **DO Droplet**: ~$10-20/month for 1GB RAM (sufficient)
- **PostgreSQL**: On same droplet (no additional cost)
- **Redis**: REMOVED - using django-background-tasks instead
- **Domain**: ~$10-15/year for .com/.id domain
- **Total**: ~$10-20/month (reduced from $15-25)

### 8.6 Alternative Considerations (Not Used)
- **Backend**: Using plain Django views (no DRF) since templates handle all UI
- **Frontend**: Django templates + Tailwind - HTMX could be added later if more dynamic features needed
- **Auth**: **Django Allauth** - chosen for easy Google OAuth integration
- **Calendar**: Manual .ics generation + Google Calendar URL (no extra library needed)
- **Hosting**: DO is fine, but Fly.io or Render could work if needed later

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low adoption | High | Promote in WhatsApp group, make it super easy to use |
| Spam events | Medium | Allow reporting, auto-archive events with no RSVPs after 7 days |
| Feature creep | Medium | Stick to MVP first, add features based on feedback |
| Deployment issues | Medium | Test Docker locally thoroughly before first deploy |
| Data loss | High | Daily backups to DO Spaces or similar |

---

## 10. Security Measures

### File Upload Security
- Allowed types: `jpg`, `jpeg`, `png`, `gif`, `webp`, `pdf`, `doc`, `docx`
- Max size: 10MB per file
- Max attachments: 5 per event
- Use secure filename (uuid + original extension)
- Serve via Django (not direct nginx) for access control

### Rate Limiting
- RSVP actions: 1 action per 5 seconds per user
- Event creation: 5 events per day per user

### Access Control
- Private events: only creator and attendees can see attendee list
- Profile visibility: public within logged-in users (cohort only)
- Admin: only superuser (you)

### Data Protection
- Debug mode: OFF in production
- SECURE_SSL_REDIRECT: True
- Session cookies: secure, httponly
- CSRF protection: enabled on all forms

---

## 11. Success Metrics

- [ ] 80% of cohort registered within 2 weeks of launch
- [ ] Average RSVP time < 30 seconds
- [ ] At least 2 events created per week
- [ ] Zero downtime in first month
- [ ] User satisfaction score > 4/5

---

*Plan created: 2026-03-08*
*For: Apple Developer Academy @ Binus Bali 2026 Cohort*
