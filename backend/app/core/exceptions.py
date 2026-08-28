class AppError(Exception):
    """Base des erreurs métier — volontairement indépendante de FastAPI :
    la couche API (app/api/*) les traduit en HTTPException, pas l'inverse."""


class EmailAlreadyRegisteredError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass


class InvalidTokenError(AppError):
    pass
