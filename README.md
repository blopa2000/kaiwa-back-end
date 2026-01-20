# ChatApp Backend

Backend for a chat application using Django Rest Framework and WebSockets (Django Channels).

## Features

- User registration and login with JWT authentication.
- Upload user profile photo directly to Cloudinary.
- Create and manage chat rooms and messages.
- Real-time messaging using WebSockets.
- User status (online, offline, typing).
- API documentation with DRF Spectacular.

## Technologies

- Python 3.11
- Django 6.0
- Django Rest Framework
- Django Channels
- Cloudinary for image storage
- Simple JWT for authentication
- DRF Spectacular for API documentation
- Daphne (optional) for production-ready ASGI server

---

## Installation

1. Clone the repository

```bash
git clone <repo-url>
cd back-chat
```

## Create and activate a virtual environment

python -m venv venv source venv/bin/activate # Linux / Mac venv\Scripts\activate # Windows

## Install dependencies

```
pip install -r requirements.txt
```

## Create a `.env` file in the root directory:

```
# ==============================
# Django
# ==============================
SECRET_KEY=django-insecure-change-this
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# ==============================
# Database (SQLite by default)
# ==============================
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# ==============================
# JWT
# ==============================
JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=1

# ==============================
# Cloudinary
# ==============================
CLOUDINARY_CLOUD_NAME=cloud_name
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
CLOUDINARY_MEDIA_FOLDER=media_folder

# ==============================
# Channels / Redis
# ==============================
CHANNEL_LAYER_BACKEND=channels.layers.InMemoryChannelLayer
REDIS_HOST=redis
REDIS_PORT=6379

# ==============================
# Localization
# ==============================
LANGUAGE_CODE=en-us
TIME_ZONE=UTC

```

## Run migrations

```
python manage.py makemigrations
python manage.py migrate
```

## Create a superuser (optional)

`python manage.py createsuperuser`

## Run the development server

`python manage.py runserver`

# or web socket

```
daphne -p 8000 config.asgi:application
```
