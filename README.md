# Nauman Tariq Portfolio — FastAPI Backend

High-performance, secure, and modular REST API backend for Nauman Tariq's portfolio website.

## 1. Technologies & Stack
- **Framework**: FastAPI (Python 3.11+)
- **Package Manager**: UV
- **ORM**: SQLAlchemy 2.0
- **Database**: Neon Cloud PostgreSQL (Serverless)
- **Migrations**: Alembic
- **Image Storage**: Cloudinary (with fallback local storage for testing)
- **Authentication**: JWT (HS256) + bcrypt
- **Validation**: Pydantic v2 + Pydantic-Settings

---

## 2. Directory Structure
```
backend/
├── app/
│   ├── main.py                  # App entry point, CORS, routers, lifecycle
│   ├── core/
│   │   ├── config.py            # Pydantic Settings & environment loader
│   │   ├── security.py          # Password verification & JWT creation
│   │   └── database.py          # SQLAlchemy engine, session maker, get_db
│   ├── models/                  # SQLAlchemy ORM entities
│   │   ├── base.py
│   │   ├── category.py          # 1-to-many with Project
│   │   ├── project.py
│   │   ├── contact_message.py   # Direct DB persistence (NO SMTP)
│   │   └── notification.py      # Announcements & Achievements
│   ├── schemas/                 # Pydantic validation models
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── project.py
│   │   ├── contact.py
│   │   └── notification.py
│   ├── api/                     # REST API routers
│   │   ├── auth.py              # /api/auth/login, /api/auth/me
│   │   ├── categories.py        # /api/categories
│   │   ├── projects.py          # /api/projects
│   │   ├── contacts.py          # /api/contact
│   │   ├── notifications.py     # /api/notifications
│   │   └── dashboard.py         # /api/dashboard/stats
│   ├── services/
│   │   └── cloudinary_service.py # Cloudinary upload & URL retrieval
│   └── dependencies/
│       └── auth.py              # Admin authorization dependency
├── alembic/                     # Database migrations
├── alembic.ini
├── .env                         # Real credentials (NOT committed)
├── .env.example                 # Template for deployment
├── pyproject.toml               # UV configuration & dependencies
└── README.md
```

---

## 3. Quickstart & Setup (UV)

### 1. Install UV (if not already installed)
```bash
pip install uv
```

### 2. Install Project Dependencies & Create Virtualenv
```bash
cd backend
uv sync
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Neon Cloud PostgreSQL credentials:
```bash
cp .env.example .env
```

### 4. Run Database Migrations
```bash
uv run alembic upgrade head
```

### 5. Start Development Server
```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Swagger documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 4. API Endpoints Overview

### Public Endpoints:
- `GET /` — API Health status
- `GET /api/categories` — Fetch all categories with project counts
- `GET /api/projects` — Fetch projects with optional `?category_slug=` filter
- `GET /api/projects/{id}` — Fetch specific project detail
- `POST /api/contact` — Submit visitor message to database (NO SMTP)
- `GET /api/notifications` — Fetch active notifications (for popup & navbar bell)

### Admin Endpoints (Require `Authorization: Bearer <token>`):
- `POST /api/auth/login` — Admin login
- `GET /api/auth/me` — Verify authenticated admin
- `GET /api/dashboard/stats` — Overview counters & latest messages
- `POST /api/categories` — Create category
- `PUT /api/categories/{id}` — Update category
- `DELETE /api/categories/{id}` — Delete category
- `POST /api/projects` — Create project
- `POST /api/projects/upload-image` — Upload image to Cloudinary
- `PUT /api/projects/{id}` — Update project
- `DELETE /api/projects/{id}` — Delete project
- `GET /api/contact/messages` — View all submitted contact messages
- `PATCH /api/contact/messages/{id}/read` — Toggle read/unread status
- `DELETE /api/contact/messages/{id}` — Permanently delete contact message
- `GET /api/notifications/all` — Fetch all notifications
- `POST /api/notifications` — Create notification
- `PUT /api/notifications/{id}` — Update notification
- `PATCH /api/notifications/{id}/status` — Toggle active/inactive
- `DELETE /api/notifications/{id}` — Delete notification
