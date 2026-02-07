# Backend Architecture (Clean Architecture)

## Top-level structure

- **app** — configuration and app bootstrap: `config`, `db`, `redis`, `logging_config`, `main`, `backend_pre_start`, `initial_data`, `tests_pre_start`, `utils`, `alembic`, `email-templates`.
- **transport** — HTTP API: routes, request/response schemas, cookie, deps (wiring use cases to infrastructure).
- **use_cases** — application layer: ports (interfaces) and use cases (Auth, Password, User, GoogleAuth).
- **domain** — entities, value objects, exceptions (no dependencies on outer layers).
- **infrastructure** — persistence (Postgres session, UoW, repositories, DB models), Redis, JWT, email, passwords, sync helpers for scripts/tests.

## Layers (dependency rule: inner layers do not depend on outer)

### 1. **Domain** (`app/domain`)
- **Entities** (`app/domain/entities`): `User`, `Item` — pure Pydantic models, no DB/ORM.
- **Value objects** (`app/domain/value_objects.py`): `UserId`, `Email`.
- **Exceptions** (`app/domain/exceptions.py`): `DomainException`, `UserNotFoundError`, `InvalidCredentialsError`, `InactiveUserError`, `UserAlreadyExistsError`.
- No dependencies on use_cases, infrastructure, or transport.

### 2. **Use cases** (`app/use_cases`)
- **Ports** (`app/use_cases/ports`): abstract interfaces  
  `ITokenService`, `IRefreshTokenStore`, `IUserRepository`, `IUnitOfWork`, `IEmailSender`.
- **Use cases** (`app/use_cases/use_cases`):  
  `AuthUseCase`, `PasswordUseCase`, `UserUseCase`, `GoogleAuthUseCase`.  
  Depend only on ports and domain; raise domain exceptions; transport maps them to HTTP.
- **Token helpers** (`app/use_cases/use_cases/token_helpers.py`): `create_and_store_tokens` (uses ports only).

### 3. **Infrastructure** (`app/infrastructure`)
- **Persistence** (`app/infrastructure/persistence`): DB models (`models.py`), Postgres `session`, `UnitOfWork`, `UserRepository` (implements ports).
- **Redis** (`app/infrastructure/redis`): `RedisRepository`, `get_redis_repo` (implements `IRefreshTokenStore`).
- **JWT** (`app/infrastructure/jwt`): `TokenService`, `get_token_service` — all token logic.
- **Email** (`app/infrastructure/email`): `EmailSender` (implements `IEmailSender`; uses `app.utils` for SMTP/templates).
- **Passwords** (`app/infrastructure/passwords`): `get_password_hash`, `verify_password`.
- **Users** (`app/infrastructure/users`): `create_user_sync`, `get_user_by_email_sync`, `update_user_sync`, `authenticate_user_sync` (for scripts and tests).

### 4. **Transport** (`app/transport`)
- **HTTP** (`app/transport/http`):  
  - **deps.py**: wires infrastructure to use cases (`get_async_session`, `get_uow`, `get_token_service`, `get_redis_repo`, `get_*_use_case`, `get_current_user`, `get_current_active_superuser`).  
  - **router.py**: composes all route modules (users, admin, items, utils).  
  - **cookie.py**: refresh token cookie helpers.  
  - **routes/**: admin, items, users (auth, passwords, google_auth), utils.
- **Schemas** (`app/transport/schemas`): request/response DTOs (Message, UserCreate, UserPublic, TokenResponse, ItemCreate, ItemPublic, etc.).
- Routes call use cases and map domain exceptions to HTTP (or rely on `app.main` exception handlers).

### 5. **App** (`app/`)
- **main.py**: creates FastAPI app, middleware, includes router, **domain exception handlers** (map to HTTP).
- **config.py**: `settings` (env, DB, Redis, JWT, email).
- **db.py**: sync engine and `init_db` for scripts (`initial_data`, tests).
- **redis.py**: Redis client for scripts.
- **logging_config.py**: `setup_logging`.
- **bootstrap.py**: documents composition root.

## Models

- **DB models** (`app/infrastructure/persistence/models.py`): SQLModel `table=True` only (User, Item). Used by repositories and Alembic.
- **Transport schemas** (`app/transport/schemas`): request/response DTOs (UserCreate, UserPublic, TokenResponse, SessionOut, ItemCreate, ItemPublic, etc.).
- **Domain entities** (`app/domain/entities`): pure domain User, Item (no ORM).

## Dependency injection (FastAPI)

- `get_async_session` → `AsyncSession` (from `app.infrastructure.persistence.postgres.session`).
- `get_uow(session)` → `UnitOfWork(session)`.
- `get_token_service()` → `TokenService`.
- `get_redis_repo()` → `RedisRepository`.
- `get_email_sender()` → `EmailSender`.
- Use cases: `get_auth_use_case`, `get_password_use_case`, `get_user_use_case`, `get_google_auth_use_case` (receive ports via Depends).

## Async

- Transport and persistence use **async** everywhere.
- Sync session/engine in `app/db.py` only for scripts (`initial_data`, `init_db`) and tests.
