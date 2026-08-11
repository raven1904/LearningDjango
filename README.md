# TaskFlow API
TaskFlow provides a structured API for managing users, projects, tasks, authentication, permissions, and task workflows while following RESTful API design principles.
---

## Features

### Authentication & Authorization

* User registration and authentication
* Token-based authentication
* Secure password handling
* Authenticated API endpoints
* User-specific data access
* Permission-based access control

### Task Management

* Create, retrieve, update, and delete tasks
* Task status management
* Task priorities
* Task assignment
* Due dates
* Task filtering and searching
* Pagination for large result sets

### Project Management

* Create and manage projects
* Organize tasks by project
* Project membership
* Project-level permissions

### API Engineering

* RESTful endpoint design
* Django REST Framework serializers
* ViewSets and routers
* Validation and consistent error responses
* Filtering, searching, and ordering
* Pagination
* Proper HTTP status codes

### Production-Oriented Engineering

* PostgreSQL database
* Environment-based configuration
* Dockerized development environment
* Automated testing
* API documentation
* Git/GitHub workflow
* CI/CD-ready project structure

---

## Tech Stack

| Layer             | Technology                     |
| ----------------- | ------------------------------ |
| Language          | Python                         |
| Framework         | Django                         |
| API Framework     | Django REST Framework          |
| Database          | PostgreSQL                     |
| Authentication    | JWT                            |
| Containerization  | Docker                         |
| API Testing       | Postman                        |
| Version Control   | Git & GitHub                   |
| Testing           | Django Test Framework / pytest |
| API Documentation | OpenAPI / Swagger              |
| Deployment        | Cloud-ready                    |

---

## Architecture

The application follows Django's modular architecture with a clear separation between responsibilities.

```text
Client
  │
  ▼
REST API
  │
  ├── Authentication
  │
  ├── Permissions
  │
  ├── Serializers
  │
  ├── Views / ViewSets
  │
  ├── Business Logic
  │
  ▼
Django ORM
  │
  ▼
PostgreSQL
```

The project is structured to keep individual applications focused on specific domains rather than putting all functionality into a single Django app.

---

## Project Structure

```text
taskflow-api/
│
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── users/
│   ├── projects/
│   └── tasks/
│
├── tests/
│
├── docker/
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

> The exact structure may evolve as the project grows.

---

## API Design

Example API resources:

```text
/api/v1/auth/
/api/v1/users/
/api/v1/projects/
/api/v1/tasks/
```

Example task endpoints:

```text
GET     /api/v1/tasks/
POST    /api/v1/tasks/
GET     /api/v1/tasks/{id}/
PATCH   /api/v1/tasks/{id}/
DELETE  /api/v1/tasks/{id}/
```

Example project endpoints:

```text
GET     /api/v1/projects/
POST    /api/v1/projects/
GET     /api/v1/projects/{id}/
PATCH   /api/v1/projects/{id}/
DELETE  /api/v1/projects/{id}/
```

The API uses appropriate HTTP methods and status codes and is versioned to make future API evolution easier.

---

## Database Model

The core domain revolves around users, projects, and tasks.

```text
User
 │
 ├───────────────┐
 │               │
 ▼               ▼
Project        Task
 │               │
 └───────────────┘
```

A project can contain multiple tasks, while tasks can be assigned to users according to the application's permission rules.

The database design will prioritize:

* Referential integrity
* Appropriate relationships
* Database constraints
* Indexing
* Query efficiency
* Data validation

---

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd taskflow-api
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Configure the required environment variables.

Example:

```env
DEBUG=True

SECRET_KEY=your-secret-key

POSTGRES_DB=taskflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 3. Start the application

Using Docker:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000/
```

### 4. Run migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

---

## API Testing

The API is tested using **Postman** during development.

Testing covers:

* Authentication flows
* CRUD operations
* Validation errors
* Authorization
* Permissions
* Edge cases
* HTTP status codes
* Filtering and pagination

A Postman collection can be included in the repository for easy API exploration.

---

## Testing

Run the test suite with:

```bash
python manage.py test
```

or, if pytest is configured:

```bash
pytest
```

The test suite aims to cover both successful requests and failure scenarios.

Example areas:

```text
Authentication
    ├── Registration
    ├── Login
    └── Token validation

Projects
    ├── CRUD
    ├── Permissions
    └── Membership

Tasks
    ├── CRUD
    ├── Assignment
    ├── Validation
    └── Permissions
```

---

## API Documentation

The API will expose interactive documentation using OpenAPI.

Documentation will allow developers to:

* Explore available endpoints
* Inspect request schemas
* Inspect response schemas
* Understand authentication requirements
* Test endpoints interactively

---

## Security

Security is treated as a first-class concern.

The project follows practices such as:

* Password hashing through Django's authentication system
* JWT-based authentication
* Permission checks
* Environment variables for secrets
* CSRF protection where applicable
* Input validation
* Restricted access to protected resources
* Production-safe configuration

Sensitive credentials should **never** be committed to the repository.

---