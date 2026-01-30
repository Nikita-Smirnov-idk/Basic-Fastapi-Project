"""
App composition root: where config and dependencies are wired.

- Config: app.config.settings (loaded from env)
- Transport deps: app.transport.http.deps (get_uow, get_token_service, get_*_use_case)
  wires infrastructure (UnitOfWork, RedisRepository, TokenService, EmailSender)
  to application use cases (AuthUseCase, PasswordUseCase, UserUseCase, GoogleAuthUseCase)
- Router: app.transport.http.router.api_router (included in app.main with prefix API_V1_STR)
- FastAPI app: app.main.app (middleware, exception handlers, router)
"""
