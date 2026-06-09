# Mini Blog FastAPI Learning Project

This repository is a full-stack learning project built as part of a FastAPI course from DevTalles. It contains a FastAPI backend for a mini blog API and a small Vite/React frontend used to test CORS and API connectivity.

The project focuses on practical FastAPI concepts: routing, request validation, SQLAlchemy models, SQLite persistence, JWT authentication, role-based authorization, file uploads, static media serving, pagination, seed data, and a simple browser client.

## Repository Layout

```text
.
+-- backend/
|   +-- app/
|   |   +-- api/
|   |   |   +-- auth/
|   |   |   +-- categories/
|   |   |   +-- posts/
|   |   |   +-- tags/
|   |   |   +-- uploads/
|   |   +-- core/
|   |   +-- media/
|   |   +-- models/
|   |   +-- seeds/
|   |   +-- services/
|   |   +-- utils/
|   |   +-- main.py
|   +-- blog.db
|   +-- requirements.txt
+-- frontend/
|   +-- public/
|   +-- src/
|   +-- package.json
|   +-- vite.config.js
+-- .gitignore
+-- README.md
```

## Backend Overview

The backend is a FastAPI application named `Mini Blog`. The application factory is defined in `backend/app/main.py`.

Main backend responsibilities:

- Creates the SQLite database schema with SQLAlchemy metadata on startup.
- Registers CORS and request middleware.
- Exposes auth, posts, uploads, tags, and categories routers.
- Serves uploaded files from `/media`.
- Stores local media files in `backend/app/media`.

### Backend Technologies

- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- PyJWT
- python-dotenv
- python-multipart
- Typer
- SQLite

### Backend Configuration

The backend reads environment variables with `python-dotenv`.

Supported configuration:

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | SQLite connection URL. The app only accepts SQLite URLs. | Absolute SQLite URL for `backend/blog.db` |
| `SECRET_KEY` | JWT signing key. | `change-me-in-prod-use-a-long-secret-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes. | `30` |
| `MAX_UPLOAD_MB` | Maximum uploaded image size. | `10` |

The local `.env`, virtual environment, Python cache files, and `blog.db` are ignored by Git.

### Database Models

The API uses SQLAlchemy ORM models:

| Model | Table | Purpose |
| --- | --- | --- |
| `UserORM` | `users` | Stores email, hashed password, full name, role, active status, and creation date. |
| `PostORM` | `posts` | Stores title, content, unique slug, image URL, author, category, and creation date. |
| `CategoryORM` | `categories` | Stores category name and slug. |
| `TagORM` | `tags` | Stores reusable tag names. |
| `post_tags` | `post_tags` | Many-to-many association table between posts and tags. |

Relationships:

- A user can own many posts.
- A category can contain many posts.
- A post can have many tags.
- A tag can belong to many posts.

The existing local SQLite database currently contains seeded users, categories, and tags, but no posts.

## API Surface

Only the authentication router is mounted under `/api/v1`. Posts, categories, tags, uploads, and media are mounted at root-level prefixes.

### Authentication

Auth routes are mounted under `/api/v1/auth`.

| Method | Path | Description | Access |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Creates a new user. | Public |
| `POST` | `/api/v1/auth/login` | Logs in with email and password and returns a JWT token plus user data. | Public |
| `POST` | `/api/v1/auth/token` | OAuth2-compatible token endpoint. | Public |
| `GET` | `/api/v1/auth/me` | Returns the current authenticated user. | Authenticated |
| `PUT` | `/api/v1/auth/role/{user_id}` | Updates a user's role. | Admin |

Passwords are hashed with PBKDF2-HMAC-SHA256. JWT tokens are signed with HS256.

Supported roles:

- `user`
- `editor`
- `admin`

### Posts

Post routes are mounted under `/posts`.

| Method | Path | Description | Access |
| --- | --- | --- | --- |
| `GET` | `/posts` | Lists posts with pagination, search, sorting, and direction. | Public |
| `GET` | `/posts/by-tags` | Lists posts matching one or more tag names. | Public |
| `GET` | `/posts/{post_id}` | Returns a post by ID. Supports `include_content`. | Public |
| `GET` | `/posts/post/{slug}` | Returns a post by slug. Supports `include_content`. | Public |
| `POST` | `/posts` | Creates a post from multipart form data and optional image upload. | Authenticated |
| `PUT` | `/posts/{post_id}` | Updates a post title or content. | Authenticated |
| `DELETE` | `/posts/{post_id}` | Deletes a post. | Authenticated |

Post listing query parameters:

- `search`: searches post titles by prefix, minimum 3 characters.
- `text`: deprecated alias-style search parameter.
- `page`: page number, starting at 1.
- `per_page`: results per page, from 1 to 50.
- `order_by`: `id` or `title`.
- `direction`: `asc` or `desc`.

Post creation accepts multipart form fields:

- `title`
- `content`
- `category_id`
- `tags`
- `image`

The `tags` field can contain comma-separated values. Uploaded post images are saved locally and returned as `/media/{filename}` URLs.

### Categories

Category routes are mounted under `/categories`.

| Method | Path | Description | Access |
| --- | --- | --- | --- |
| `GET` | `/categories` | Lists categories with `skip` and `limit`. | Public |
| `POST` | `/categories` | Creates a category. | Public |
| `GET` | `/categories/{category_id}` | Gets a category by ID. | Public |
| `PUT` | `/categories/{category_id}` | Updates a category. | Public |
| `DELETE` | `/categories/{category_id}` | Deletes a category. | Public |

Categories use unique names and slugs.

### Tags

Tag routes are mounted under `/tags`.

| Method | Path | Description | Access |
| --- | --- | --- | --- |
| `GET` | `/tags` | Lists tags with pagination, search, sorting, and direction. | Public |
| `POST` | `/tags` | Creates a tag if it does not already exist. | Editor or Admin |
| `PUT` | `/tags/{tag_id}` | Updates a tag. | Editor or Admin |
| `DELETE` | `/tags/{tag_id}` | Deletes a tag. | Admin |
| `GET` | `/tags/popular/top` | Returns the most-used tag. | Authenticated user |

Tag listing query parameters:

- `page`
- `per_page`
- `search`
- `order_by`: `id` or `name`
- `direction`: `asc` or `desc`

### Uploads and Media

Upload routes are mounted under `/upload`.

| Method | Path | Description | Access |
| --- | --- | --- | --- |
| `POST` | `/upload/save` | Saves a PNG or JPEG file and returns metadata. | Public |

Upload behavior:

- Accepts only `image/png` and `image/jpeg`.
- Saves files under `backend/app/media`.
- Generates unique filenames with UUIDs.
- Enforces `MAX_UPLOAD_MB`.
- Serves saved files through `/media/{filename}`.
- Returns file metadata such as filename, content type, size, chunk size, and chunk call counts.

## Middleware

The backend registers several middleware layers:

- CORS is open to all origins, methods, and headers.
- `X-Process-Time` is added to responses.
- `X-Request-ID` is added to responses.
- Basic request and response logging is printed to the console.
- A simple in-memory IP blacklist hook exists through `BLACKLIST`.

## Seeds

The backend includes a Typer-based seed CLI in `backend/app/seeds`.

Seeded data includes:

- Users for `admin`, `editor`, and `user` roles.
- Additional demo users related to the course context.
- Categories such as Python, FastAPI, SQLAlchemy, Django, Flask, JavaScript, Golang, and Laravel.
- Tags such as python, fastapi, backend, apis, frontend, javascript, and cloud.

Available seed commands:

```bash
cd backend
python -m app.seeds all
python -m app.seeds users
python -m app.seeds categories
python -m app.seeds tags
```

Demo users from the seed file:

| Email | Role |
| --- | --- |
| `admin@example.com` | `admin` |
| `editor@example.com` | `editor` |
| `user@example.com` | `user` |
| `ricardo@example.com` | `admin` |
| `fernando@example.com` | `editor` |
| `juanperez@example.com` | `user` |

## Frontend Overview

The frontend is a Vite/React application named `cors-demo`.

Its current UI is a simple CORS connection demo:

- Shows a page titled `Demo CORS con FastAPI`.
- Includes a button labeled `Probar conexion`.
- Calls `http://127.0.0.1:8000/posts`.
- Prints the JSON response when the backend is reachable.
- Shows an error message when CORS or connectivity fails.

Frontend technologies:

- React 19
- React DOM
- Vite
- ESLint

Frontend assets include:

- `frontend/public/favicon.svg`
- `frontend/public/icons.svg`
- `frontend/src/assets/hero.png`
- `frontend/src/assets/react.svg`
- `frontend/src/assets/vite.svg`

## Getting Started

### 1. Backend Setup

From the repository root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional `.env` example:

```env
SECRET_KEY=replace-this-with-a-long-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///blog.db
MAX_UPLOAD_MB=10
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive docs:

```text
http://127.0.0.1:8000/docs
```

### 2. Load Seed Data

With the backend virtual environment active:

```bash
cd backend
python -m app.seeds all
```

### 3. Frontend Setup

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server will print the local URL, usually:

```text
http://127.0.0.1:5173
```

Use the `Probar conexion` button to call the FastAPI `/posts` endpoint.

## Useful Commands

Backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
python -m app.seeds all
```

Frontend:

```bash
cd frontend
npm run dev
npm run build
npm run lint
npm run preview
```

## Notes

- This is a learning repository, not a production-ready application.
- The backend currently creates database tables directly with `Base.metadata.create_all`.
- There are no migration files.
- The frontend is intentionally minimal and is mainly used to verify CORS and API connectivity.
- Authentication is implemented in the backend, but the frontend does not currently include login or token handling.
- The uploaded media directory contains local runtime files and should be treated as development data.
- The root `.gitignore` ignores local environment files, Python virtual environments, cache files, and the SQLite database.
