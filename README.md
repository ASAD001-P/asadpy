# AsadPy - Asynchronous FastAPI Store Engine

A production-ready asynchronous Python REST API built with FastAPI, SQLModel, Alembic, and PostgreSQL, fully containerized with Docker and deployed on Render.

## 🚀 Live Demo & Endpoints
* **Base API**: https://asadpy-api.onrender.com
* **Interactive Docs**: https://asadpy-api.onrender.com/docs
* **Health Check**: https://asadpy-api.onrender.com/health

## 🌟 Key Features
* **Asynchronous ORM**: High-performance database operations using `SQLModel` and `asyncpg`.
* **Database Migrations**: Automatic schema version control managed by `Alembic`.
* **Security**: Argon2id password hashing and OAuth2 Bearer JWT authentication.
* **Rate Limiting**: Protected authentication routes via `slowapi` to mitigate brute-force attacks.
* **Containerization**: Dockerized multi-stage builds running in production.
* **CI/CD Pipeline**: GitHub Actions running `pytest` test suites on every pull request.

## 🛠️ Tech Stack
- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLModel / SQLAlchemy
- **Containerization**: Docker
- **Hosting**: Render & Vercel
