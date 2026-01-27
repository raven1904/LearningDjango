# Learning Django

A Django learning project exploring the fundamentals of web development with Django.

## Project Structure

```
LearningDjango/
├── mysite/                 # Main Django project
│   ├── manage.py          # Django management script
│   ├── db.sqlite3         # SQLite database
│   │
│   ├── mysite/            # Project configuration
│   │   ├── settings.py    # Project settings
│   │   ├── urls.py        # URL routing
│   │   ├── wsgi.py        # WSGI application
│   │   └── asgi.py        # ASGI application
│   │
│   └── core/              # Main application
│       ├── models.py      # Database models
│       ├── views.py       # View logic
│       ├── urls.py        # App-level routing
│       ├── admin.py       # Admin configuration
│       ├── apps.py        # App configuration
│       ├── migrations/    # Database migrations
│       └── templates/
│           └── core/
│               └── home.html
```

## Getting Started

### Prerequisites

- Python 3.x
- Django

### Installation

1. Navigate to the project directory:
   ```bash
   cd mysite
   ```

2. Install dependencies:
   ```bash
   pip install django
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

### Running the Server

Start the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

## Applications

### core
The main application containing:
- **Models**: Database schema definitions
- **Views**: Request handlers and response logic
- **Templates**: HTML templates for rendering pages
- **Admin**: Django admin interface configuration

## Learning Topics Covered

- Django project setup and configuration
- App creation and organization
- URL routing (project and app-level)
- Views and templates
- Models and database structure
- Django admin interface
- Static files and templates

## Database

This project uses SQLite (`db.sqlite3`) for development. The database schema is managed through Django migrations.

## License

See the [LICENSE](LICENSE) file for details.

## Notes

This is a learning project for exploring Django fundamentals and best practices.
